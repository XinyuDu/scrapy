-- 连接到您的TeslaMate数据库，执行以下SQL
CREATE OR REPLACE FUNCTION notify_new_drive()
  RETURNS trigger AS
$$
BEGIN
  -- 使用 pg_notify 发送通知，并将新记录的ID作为payload
  PERFORM pg_notify('new_drive', NEW.id::text);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 确保触发器存在，并关联到drives表
DROP TRIGGER IF EXISTS drive_insert_trigger ON drives;
CREATE TRIGGER drive_insert_trigger
  AFTER INSERT ON drives
  FOR EACH ROW
  EXECUTE FUNCTION notify_new_drive();

SELECT event_object_table AS 表名,
       trigger_name AS 触发器名称,
       event_manipulation AS 触发事件,
       action_statement AS 触发操作
FROM information_schema.triggers;

-- 创建审计表
CREATE TABLE drive_audit (
    id SERIAL PRIMARY KEY,
    operation CHAR(1) NOT NULL,  -- 'I'=插入, 'U'=更新, 'D'=删除
    changed_by TEXT NOT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    old_data JSONB,
    new_data JSONB
);

-- 创建触发器函数
CREATE OR REPLACE FUNCTION log_drive_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO drive_audit (operation, changed_by, new_data)
        VALUES ('I', current_user, to_jsonb(NEW));
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO drive_audit (operation, changed_by, old_data, new_data)
        VALUES ('U', current_user, to_jsonb(OLD), to_jsonb(NEW));
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO drive_audit (operation, changed_by, old_data)
        VALUES ('D', current_user, to_jsonb(OLD));
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER drive_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON drives
FOR EACH ROW EXECUTE FUNCTION log_drive_changes();


-- 第一步：删除触发器
DROP TRIGGER IF EXISTS drive_change_trigger ON drives;

-- 第二步：删除触发器函数
DROP FUNCTION IF EXISTS notify_drive_change();

-- 创建触发器函数，并将记录放入payload中返回。
CREATE OR REPLACE FUNCTION notify_table_change()
RETURNS TRIGGER AS $$
DECLARE
    payload_json JSON;
BEGIN
    -- 构建一个包含操作类型和完整记录的JSON对象
    payload_json = json_build_object(
        'operation', TG_OP,      -- 操作类型: INSERT, UPDATE, DELETE
        'schema', TG_TABLE_SCHEMA, -- 模式名
        'table', TG_TABLE_NAME,  -- 表名
        'record', CASE           -- 记录数据
            WHEN TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN row_to_json(NEW)
            WHEN TG_OP = 'DELETE' THEN row_to_json(OLD)
        END,
        'timestamp', CURRENT_TIMESTAMP  -- 时间戳
    );

    -- 使用 pg_notify 发送通知到频道 'table_changes'
    -- 第二个参数是文本格式的JSON
    PERFORM pg_notify('table_changes', payload_json::text);

    -- 根据触发器规则返回合适的行
    -- 对于 AFTER 触发器，通常返回 NULL 或受影响的记录（NEW/OLD）均可
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- 创建触发器，在插入、更新或删除操作之后执行
CREATE TRIGGER drive_change_trigger
AFTER INSERT OR UPDATE OR DELETE ON drives
FOR EACH ROW EXECUTE FUNCTION notify_table_change();