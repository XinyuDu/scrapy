from sqlalchemy import create_engine, text
from pushplus import pushplus
from datetime import datetime, timedelta
import uuid
import os
import pandas as pd

def get_state():
    sql_statement = text("""SELECT * FROM "public"."states" WHERE state='online' ORDER BY "start_date" DESC LIMIT 1 OFFSET 0;""")

    try:
        # 连接并执行查询
        with engine.connect() as connection:
            # 执行查询[6,8](@ref)
            result = connection.execute(sql_statement)

            # 获取所有结果
            results = result.fetchall()

        return results

    except Exception as e:
        print(f"操作出错: {e}")

def get_drives(start_date, end_date):
    sql_statement = text(
        """SELECT id, start_date, end_date, distance, duration_min, start_address_id, end_address_id
           FROM "public"."drives"
           WHERE start_date >= :start_date AND end_date <= :end_date
           ORDER BY "start_date" DESC;""")
    try:
        # 连接并执行查询
        with engine.connect() as connection:
            # 执行查询[6,8](@ref)
            result = connection.execute(
                sql_statement,
                {"start_date": start_date, "end_date": end_date}
            )

            # 获取所有结果
            results = result.fetchall()
            if not results:
                return None

            df = pd.DataFrame(results, columns=['drive_id',
                'start_date', 'end_date', 'distance', 'duration_min',
                'start_address_id', 'end_address_id'
            ])

            merged_data = {
                'start_id': df.loc[df['start_date'].idxmin(), 'drive_id'],
                'end_id': df.loc[df['end_date'].idxmax(), 'drive_id'],
                'start_date': df['start_date'].min(),
                'end_date': df['end_date'].max(),
                'total_distance': df['distance'].sum(),
                'total_duration_min': df['duration_min'].sum(),
                'start_address_id': df.loc[df['start_date'].idxmin(), 'start_address_id'],
                'end_address_id': df.loc[df['end_date'].idxmax(), 'end_address_id']
            }

            return merged_data

    except Exception as e:
        print(f"操作出错: {e}")

def get_addresses(address_id):
    sql_statement = text(f"""SELECT display_name FROM "public"."addresses" Where id={address_id};""")
    try:
        # 连接并执行查询
        with engine.connect() as connection:
            # 执行查询[6,8](@ref)
            result = connection.execute(sql_statement)

            # 获取所有结果
            results = result.fetchall()

            return results

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

def get_battery_consume(start_drive_id, end_drive_id):
    sql_statement = text(
        """SELECT battery_level, drive_id
           FROM "public"."positions"
           WHERE drive_id >= :start_id AND drive_id <= :end_id
           ORDER BY "drive_id" DESC;""")

    try:
        # 连接并执行查询
        with engine.connect() as connection:
            # 执行查询[6,8](@ref)
            result = connection.execute(
                sql_statement,
                {"start_id": start_drive_id, "end_id": end_drive_id}
            )

            # 获取所有结果
            results = result.fetchall()
            if not results:
                return None

            df = pd.DataFrame(results, columns=['battery_level', 'drive_id'])

            merged_data = {
                'start_battery_level': df['battery_level'].max(),
                'end_battery_level': df['battery_level'].min()
            }

            return merged_data

    except Exception as e:
        print(f"操作出错: {e}")

def save_last_state_id(state_id):
    with open(os.path.dirname(os.path.abspath(__file__))+'/state_id_storage.txt', 'w') as f:
        f.write(str(state_id))

def get_last_state_id():
    try:
        with open(os.path.dirname(os.path.abspath(__file__))+'/state_id_storage.txt', 'r') as f:
            id = f.readline()
            return int(id)
    except Exception as e:
        print(e)
        return False

engine = create_engine('postgresql://teslamate:123456@nas.tailc67917.ts.net:15432/teslamate')

states = get_state()
id = states[0][0]
start_date = states[0][2]
stop_date = states[0][3]
now = datetime.now()
print(now)
if id!=get_last_state_id() and stop_date!=None: ##newest id != saved id
    try:
        # drive = get_drives(start_date.strftime("%Y-%m-%d %H:%M:%S.%f"), stop_date.strftime("%Y-%m-%d %H:%M:%S.%f"))
        drive = get_drives('2025-10-16 09:26:20.488', '2025-10-16 09:46:57.669963')
        if drive is not None:
            start_time = (drive['start_date'] + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            end_time = (drive['end_date'] + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            distance = drive['total_distance']
            duration_min = drive['total_duration_min']
            start_address_id = drive['start_address_id']
            end_address_id = drive['end_address_id']
            start_address = get_addresses(start_address_id)[0][0]
            end_address = get_addresses(end_address_id)[0][0]
            avg_speed = round(distance / duration_min * 60, 2)
            start_drive_id = drive['start_id']
            end_drive_id = drive['end_id']
            battery_consume = get_battery_consume(start_drive_id.item(), end_drive_id.item())
            if battery_consume is not None:
                consume = (battery_consume['start_battery_level'] - battery_consume['end_battery_level']) / 100 * 60
                if consume > 0:
                    efficiency = round(consume / distance * 100,2)
                else:
                    efficiency = 'N/A'
            else:
                efficiency = 'None'

            send_msg(round(distance, 2), duration_min, avg_speed, efficiency, start_time, end_time,
                     start_address, end_address)
        else:
            print('drive is None.')
        save_last_state_id(id)
    except Exception as e:
        print(e)
else:
    print('id equal or stop_date=None')