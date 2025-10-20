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

SELECT event_object_table AS drives,
       trigger_name AS 触发器名称,
       event_manipulation AS 触发事件,
       action_statement AS 触发操作
FROM information_schema.triggers;
