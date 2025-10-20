import select
from datetime import timedelta
import psycopg2
from pushplus import pushplus
import uuid

def get_drives(drive_id, connection):
    try:
        with connection.cursor() as cursor:
            # 查询完整的行驶记录信息
            query = """
                    SELECT id, start_date, end_date, distance, duration_min, start_address_id, end_address_id
                    FROM drives 
                    WHERE id = %s
                    """
            cursor.execute(query, (drive_id,))
            drive_record = cursor.fetchone()

            if drive_record:
                return drive_record
            return None

    except Exception as e:
        print(f"查询行驶记录详情失败: {e}")
        return None

def get_addresses(address_id, connection):
    try:
        with connection.cursor() as cursor:
            # 查询完整的行驶记录信息
            query = """
                    SELECT display_name FROM "public"."addresses" Where id=%s;
                    """
            cursor.execute(query, (address_id,))
            address_record = cursor.fetchone()

            if address_record:
                # # 获取列名并创建字典
                # colnames = [desc[0] for desc in cursor.description]
                # drive_dict = dict(zip(colnames, drive_record))
                # drive_dict['fetch_time'] = datetime.now().isoformat()
                # return drive_dict
                return address_record

            return None

    except Exception as e:
        print(f"查询地址详情失败: {e}")
        return None

def get_efficiency(drive_id, distance, connection):
    if distance == 0 :
        return 'distance == 0'

    try:
        with connection.cursor() as cursor:
            query = """SELECT
                            drive_id,
                            MAX(battery_level) AS max_battery_level,
                            MIN(battery_level) AS min_battery_level
                        FROM "public"."positions"
                        WHERE drive_id = %s
                        GROUP BY drive_id;"""
            cursor.execute(query, (drive_id,))
            position_records = cursor.fetchone()

            if len(position_records) > 0:
                efficiency =  (position_records[1] - position_records[2]) * 60 / distance
                if efficiency > 0:
                    return str(round(efficiency,2))
                else:
                    return 'N/A'

            return 'N/A'

    except Exception as e:
        print(f"操作出错: {e}")

def send_msg(distance, duration_min, avg_speed, efficiency, start_time, end_time, start_address, end_address):
    content = "距离：{} 公里\n耗时：{} 分钟\n均速：{} 公里/小时\n能耗：{} 度/百公里\n出发时间：{}\n到达时间：{}\n起始地点：{}\n到达地点：{}".format(distance, duration_min, avg_speed, efficiency, start_time, end_time, start_address, end_address,)

    body = {
        "token": "2cfba23c342a4deeba50a6d922ec2ea4",
        "content": content+ '\n'+ str(uuid.uuid4()),
        "title": "驾驶旅程信息",
    }
    msg = pushplus(body)
    re = msg.send()
    print(re.text)

def listen_and_fetch():
    # 数据库连接参数，请根据你的TeslaMate数据库配置修改
    conn_params = {
        'dbname': 'test',
        'user': 'teslamate',
        'password': '123456',  # 请替换为你的密码
        'host': 'nas.tailc67917.ts.net',
        'port': '15432'
    }

    conn = None
    try:
        # 建立数据库连接
        conn = psycopg2.connect(**conn_params)
        # 设置连接为自动提交模式，这对于LISTEN是必须的[11](@ref)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        curs = conn.cursor()

        # 开始监听频道 'new_drive'
        curs.execute("LISTEN new_drive;")
        print("开始监听数据库通知... 等待新的行驶记录。")

        while True:
            # 等待并处理通知
            # 使用select等待5秒，避免忙等待[11](@ref)
            if select.select([conn], [], [], 5) == ([], [], []):
                # 超时，可以在这里执行一些定期任务或保持连接活性
                # print("监听中...")
                pass
            else:
                # 有通知或连接活动
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    drive_id = notify.payload  # 这里就是从触发器收到的 drive_id
                    print(f"收到通知，行驶记录ID: {drive_id}")
                    drive = get_drives(drive_id, conn)
                    start_time = (drive[1] + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                    end_time = (drive[2] + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                    distance = drive[3]
                    duration_min = drive[4]
                    start_address_id = drive[5]
                    end_address_id = drive[6]
                    start_address = get_addresses(start_address_id, conn)[0]
                    end_address = get_addresses(end_address_id, conn)[0]
                    avg_speed = round(distance / duration_min * 60, 2)
                    efficiency = get_efficiency(drive_id, distance)
                    send_msg(round(distance, 2), duration_min, avg_speed, efficiency, start_time, end_time,
                     start_address, end_address)

    except Exception as e:
        print(f"监听过程中出现错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    listen_and_fetch()