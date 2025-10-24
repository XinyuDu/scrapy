import select
from datetime import timedelta, datetime
import psycopg2
from pushplus import pushplus
import uuid
import json

def update_cost(update_id, cost, connection):
    try:
        with connection.cursor() as cursor:
            query = """UPDATE "public"."charging_processes" SET cost = %s WHERE id = %s;"""
            cursor.execute(query, (cost, update_id))
            affected_rows = cursor.rowcount
            # 提交事务
            connection.commit()
            # 根据影响行数返回结果
            return affected_rows > 0

    except Exception as e:
        # 发生异常时回滚事务
        print(f"更新cost失败: {e}")
        connection.rollback()
        return False

def get_addresses(address_id, connection):
    try:
        with connection.cursor() as cursor:
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

def get_journey_time_by_drive_id(drive_id, connection):
    ## 通过drive_id查询positions表，查出最早和最晚speed=0的时间
    ## 从而精确的获得旅程起始和结束时间，以弥补drive表中start_date
    ## 和end_date时间不准确的问题。
    try:
        with connection.cursor() as cursor:
            query = """
                    SELECT 
                        drive_id,
                        MIN(date) AS earliest_zero_speed_time,
                        MAX(date) AS latest_zero_speed_time
                    FROM positions 
                    WHERE drive_id = %s
                        AND speed = 0
                    GROUP BY drive_id;
                    """
            cursor.execute(query, (drive_id,))
            drive_time = cursor.fetchone()

            if drive_time:
                return drive_time

            return None

    except Exception as e:
        print(f"查询positions表出现错误: {e}")
        return None

def send_msg(title, content):
    body = {
        "token": "2cfba23c342a4deeba50a6d922ec2ea4",
        "content": content,
        "title": title,
    }
    msg = pushplus(body)
    re = msg.send()
    print(re.text)

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
                    try:
                        if operation == 'UPDATE' and table_name == 'drives':
                            drive_record = payload['record']
                            drive_id = drive_record['id']
                            position_record = get_journey_time_by_drive_id(drive_id, conn)
                            start_time = (position_record[1] + timedelta(hours=8)).strftime(
                                "%Y-%m-%d %H:%M:%S")
                            end_time = (position_record[2] + timedelta(hours=8)).strftime(
                                "%Y-%m-%d %H:%M:%S")
                            distance = drive_record['distance']
                            duration_min = drive_record['duration_min']
                            if duration_min==0:
                                print("duration_min=0, 忽略")
                                continue
                            duration = timedelta(seconds=int((position_record[2] - position_record[1]).total_seconds()))
                            avg_speed = round(distance / duration.total_seconds() * 3600, 2)
                            start_address_id = drive_record['start_address_id']
                            end_address_id = drive_record['end_address_id']
                            start_address = get_addresses(start_address_id, conn)[0]
                            end_address = get_addresses(end_address_id, conn)[0]
                            efficiency = get_efficiency(drive_id, distance, conn)
                            content = "距离：{} 公里\n耗时：{}\n均速：{} 公里/小时\n能耗：{} 度/百公里\n出发时间：{}\n到达时间：{}\n起始地点：{}\n到达地点：{}".format(
                                round(distance, 2), duration, avg_speed, efficiency, start_time, end_time, start_address, end_address)
                            content = content + '\n' + str(uuid.uuid4())
                            title = "驾驶旅程信息"
                            send_msg(title, content)
                        elif operation == 'UPDATE' and table_name == 'charging_processes':
                            charging_record = payload['record']
                            cost = charging_record['cost']
                            if cost != None:
                                print("cost != None, 忽略")
                                continue
                            address_id = charging_record['address_id']
                            start_time = (datetime.strptime(charging_record['start_date'], '%Y-%m-%dT%H:%M:%S.%f') + timedelta(
                                hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                            end_time = (datetime.strptime(charging_record['end_date'], '%Y-%m-%dT%H:%M:%S.%f') + timedelta(
                                hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                            duration_min = charging_record['duration_min']
                            duration = timedelta(minutes=duration_min)
                            outside_temp_avg = charging_record['outside_temp_avg']
                            charge_energy_added = charging_record['charge_energy_added']
                            charge_energy_used = charging_record['charge_energy_used']
                            efficiency = round(charge_energy_added/charge_energy_used*100,1)
                            address = get_addresses(address_id, conn)[0]
                            start_battery_level = charging_record['start_battery_level']
                            end_battery_level = charging_record['end_battery_level']
                            start_ideal_range_km = charging_record['start_ideal_range_km']
                            end_ideal_range_km = charging_record['end_ideal_range_km']
                            if address_id == 1 and charge_energy_used != None:
                                cost = round(charge_energy_used * 0.4733,2)
                                update_cost(charging_record['id'], cost,conn)
                            else:
                                cost = 'N/A'
                            content = "花费：{} 元\n充电：{} 度，耗电：{} 度，效率：{}%\n电池：{}% → {}%\n里程：{} → {} 公里\n温度：{}℃\n开始：{}\n结束：{}\n耗时：{}\n地址：{}".format(
                                    cost, charge_energy_added,charge_energy_used,efficiency, start_battery_level, end_battery_level, start_ideal_range_km, end_ideal_range_km,
                                outside_temp_avg, start_time, end_time, duration, address)
                            title = "充电信息"
                            send_msg(title, content)
                        else:
                            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), operation, table_name)
                    except Exception as e:
                        print(f"处理消息发生错误", {e})

    except Exception as e:
        print(f"监听过程中出现错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    listen_and_fetch()
