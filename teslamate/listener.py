import select
from datetime import timedelta, datetime
import psycopg2
from pushplus import pushplus
import uuid
import json

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
        print(f"计算能耗操作出错: {e}")
        return 'N/A'

def send_msg(title, content):
    body = {
        "token": "2cfba23c342a4deeba50a6d922ec2ea4",
        "content": content,
        "title": title,
    }
    msg = pushplus(body)
    re = msg.send()
    print(re.text)


def convert_minutes(total_minutes):
    """
    将分钟数转换为小时和分钟的格式。

    参数:
        total_minutes (int): 总分钟数

    返回:
        str: 格式化后的字符串，格式为"X小时Y分钟"
    """
    hours = total_minutes // 60
    minutes = total_minutes % 60
    # 根据小时和分钟的值，决定输出的格式
    if hours > 0 and minutes > 0:
        return f"{hours}小时{minutes}分钟"
    elif hours > 0 and minutes==0:  # 分钟数为0，只显示小时
        return f"{hours}小时"
    elif minutes > 0 and hours==0:  # 小时数为0，只显示分钟
        return f"{minutes}分钟"
    else:  # 总分钟数为0的特殊情况
        return "0分钟"

def listen_and_fetch():
    # 数据库连接参数，请根据你的TeslaMate数据库配置修改
    conn_params = {
        'dbname': 'teslamate',
        'user': 'teslamate',
        'password': '123456',  # 请替换为你的密码
        'host': 'nas.tailc67917.ts.net', #'nas.tailc67917.ts.net',
        'port': '15432'
    }

    conn = None
    try:
        # 建立数据库连接
        conn = psycopg2.connect(**conn_params)
        # 设置连接为自动提交模式，这对于LISTEN是必须的[11](@ref)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        curs = conn.cursor()

        # 开始监听频道 'table_changes'
        curs.execute("LISTEN table_changes;")
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ", 开始监听数据库通知... 等待新的行驶记录。")

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
                    payload_data = notify.payload
                    payload = json.loads(payload_data)
                    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + f", 收到通知: {payload}")
                    operation = payload['operation']
                    table_name = payload['table']
                    if operation == 'UPDATE' and table_name == 'drives':
                        drive_record = payload['record']
                        drive_id = drive_record['id']
                        start_time = (datetime.strptime(drive_record['start_date'], '%Y-%m-%dT%H:%M:%S.%f') + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                        end_time = (datetime.strptime(drive_record['end_date'], '%Y-%m-%dT%H:%M:%S.%f') + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                        distance = drive_record['distance']
                        duration_min = drive_record['duration_min']
                        start_address_id = drive_record['start_address_id']
                        end_address_id = drive_record['end_address_id']
                        start_address = get_addresses(start_address_id, conn)[0]
                        end_address = get_addresses(end_address_id, conn)[0]
                        avg_speed = round(distance / duration_min * 60, 2)
                        efficiency = get_efficiency(drive_id, distance, conn)
                        content = "距离：{} 公里\n耗时：{}\n均速：{} 公里/小时\n能耗：{} 度/百公里\n出发时间：{}\n到达时间：{}\n起始地点：{}\n到达地点：{}".format(
                            round(distance, 2), convert_minutes(duration_min), avg_speed, efficiency, start_time, end_time, start_address, end_address)
                        content = content + '\n' + str(uuid.uuid4())
                        title = "驾驶旅程信息"
                        send_msg(title, content)
                    elif operation == 'UPDATE' and table_name == 'charging_processes':
                        charging_record = payload['record']
                        address_id = charging_record['id']
                        start_time = (datetime.strptime(charging_record['start_date'], '%Y-%m-%dT%H:%M:%S.%f') + timedelta(
                            hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                        end_time = (datetime.strptime(charging_record['end_date'], '%Y-%m-%dT%H:%M:%S.%f') + timedelta(
                            hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                        duration_min = charging_record['duration_min']
                        outside_temp_avg = charging_record['outside_temp_avg']
                        charge_energy_added = charging_record['charge_energy_added']
                        charge_energy_used = charging_record['charge_energy_used']
                        efficiency = round(charge_energy_added/charge_energy_used*100,1)
                        address = get_addresses(address_id, conn)[0]
                        start_battery_level = charging_record['start_battery_level']
                        end_battery_level = charging_record['end_battery_level']
                        start_ideal_range_km = charging_record['start_ideal_range_km']
                        end_ideal_range_km = charging_record['end_ideal_range_km']
                        if address_id == 1:
                            cost = charge_energy_used * 0.4733
                        else:
                            cost = 'N/A'
                        content = "花费：{} 元\n充电：{} 度，耗电：{} 度，效率：{}%\n电池：{}% → {}%\n里程：{} → {} 公里\n温度：{}℃\n开始：{}\n结束：{}\n耗时：{}\n地址：{}".format(
                                round(cost,2), charge_energy_added,charge_energy_used,efficiency, start_battery_level, end_battery_level, start_ideal_range_km, end_ideal_range_km,
                            outside_temp_avg, start_time, end_time, convert_minutes(duration_min), address)
                        title = "充电信息"
                        send_msg(title, content)
                    else:
                        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), operation, table_name)

    except Exception as e:
        print(f"监听过程中出现错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    listen_and_fetch()

