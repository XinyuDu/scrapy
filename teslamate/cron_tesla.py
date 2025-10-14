from sqlalchemy import create_engine, text
from pushplus import pushplus
from datetime import datetime, timedelta

def get_state():
    sql_statement = text("""
    SELECT * FROM "public"."states"
    ORDER BY "start_date" DESC
    LIMIT 1 OFFSET 0;
    """)

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

def get_drives():
    sql_statement = text(
        """SELECT start_date, end_date, distance, duration_min, start_address_id, end_address_id FROM "public"."drives" ORDER BY "start_date" DESC LIMIT 1 OFFSET 0;""")
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

def send_msg(distance, duration_min, avg_speed, start_time, end_time, start_address, end_address):
    content = "距离：{}公里\n耗时：{}分钟\n均速：{}公里/小时\n出发时间：{}\n到达时间：{}\n起始地点：{}\n到达地点：{}".format(distance, duration_min, avg_speed, start_time, end_time, start_address, end_address,)

    body = {
        "token": "2cfba23c342a4deeba50a6d922ec2ea4",
        "content": content,
        "title": "驾驶旅程信息",
    }
    msg = pushplus(body)
    re = msg.send()
    print(re.text)

engine = create_engine('postgresql://teslamate:123456@nas.tailc67917.ts.net:15432/teslamate')

states = get_state()
state = states[0][1]
start_date = states[0][2]
start_date = start_date+timedelta(hours=8)
stop_date = states[0][3]
now = datetime.now()
if (now-start_date).total_seconds()<300 and stop_date==None: #in 5min to latest start_date of offline state and stop_date is None
    drive = get_drives()
    start_time = (drive[0][0]+timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    end_time = (drive[0][1]+timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    distance = round(drive[0][2],2)
    duration_min = drive[0][3]
    start_address_id = drive[0][4]
    end_address_id = drive[0][5]
    start_address = get_addresses(start_address_id)[0][0]
    end_address = get_addresses(end_address_id)[0][0]
    avg_speed = round(distance/duration_min*60,2)
    send_msg(distance, duration_min, avg_speed, start_time, end_time, start_address, end_address)