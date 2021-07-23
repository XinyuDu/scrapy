# -*- coding: UTF-8 -*-
import pymysql

class DataMemorizer(object):
    def __init__(self):
        self.database = pymysql.connect(host="192.168.137.2", user="root", password="123qwe", db="trains")
        self.cur = self.database.cursor()

    def insertData(self, table_name, page_num, num, train_num, start, end):
        '''
        向数据库插入数据
        :param table_name:表名 
        :param erp: erp
        :param emb: 数据
        :return: 
        '''
        table = self._toChar(table_name)
        train_num = self._toStr(train_num)
        start = self._toStr(start)
        end = self._toStr(end)

        # 先要将numpy数组转换成二进制流，才能存到数据库中
        sql = "insert into " + table + "(page_num,num,train_num,start,end) values(" + page_num + "," + num + "," + train_num + "," + start + "," + end + ");"
        # print('****sql',sql)
        self.cur.execute(sql)
        self.database.commit()
        # print("已插入数据")
 
    def updateData(self, table_name, dateID, data):
        '''
        更新数据库数据
        :param table_name:表名 
        :param erp: erp
        :param emb: 需要修改成的数据
        :return: 
        '''
        table = self._toChar(table_name)
        date = self._toStr(dateID)
        if not self._hasThisId(table_name, dateID):
            # 如果没有这个主键值，那还改个屁，直接返回
            return
        # 同样也是将data这个numpy数组转换一下成二进制流数据
        b_data = data.tostring()
        sql = "update " + table + " set reward = %s where dates = %s;"
        self.cur.execute(sql, (b_data, date))
        self.database.commit()
        print("已更新数据：%s..." % dateID)

    def getAll(self,table_name):
        '''
        获取数据库全部数据
        param table_name:表名
        return: names,embs
        names:a list contain erps
        embs: a numpy array [elementnum,dim]
        '''
        table = self._toChar(table_name)
        sql = "SELECT * FROM face."+table+";"

        try:
            self.cur.execute(sql)
            results = self.cur.fetchall()
            row_num = len(results)
            names=[]
            embs=np.zeros(shape=(row_num,512),dtype=np.float32)
            for i,row in enumerate(results):
                names.append(row[1])
                t = np.frombuffer(row[2],dtype=np.float32)
                if t.shape[0]!=512:
                    print(row[1])
                # print(t.shape)
                # print(embs[i])
                embs[i,:]=t

            return names,embs

        except Exception as e:
            # 如果发生错误则回滚
            print(e)
            self.database.rollback()
            return False,False
 
    def _toChar(self, string):
        '''
        为输入的字符串添加一对反引号，用于表名、字段名等对关键字的规避
        :param string: 
        :return: 
        '''
        return "`%s`" % string
 
    def _toStr(self, string):
        '''
        为输入的字符串添加一对单引号，用于数值处理，规避字符串拼接后原字符串暴露问题
        :param string: 
        :return: 
        '''
        return "'%s'" % string
 
    def __del__(self):
        '''
        临走之前记得关灯关电关空调，还有关闭数据库资源
        :return: 
        '''
        # print(u'关闭数据库')
        self.database.close()
