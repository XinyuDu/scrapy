# -*- coding: UTF-8 -*-
import pymysql

class DataMemorizer(object):
    def __init__(self):
        self.database = pymysql.connect("192.168.8.3", "root", "123qwe", "news")
        self.cur = self.database.cursor()

    def insertData(self, table_name, stock_name, stock_date, stock_open, stock_max, stock_min,
                   stock_close, stock_change, stock_change_rate, stock_volumn_hand, stock_volumn,
                   ):

        table = self._toChar(table_name)
        stock_name = self._toStr(stock_name)
        stock_date = self._toStr(stock_date)
        stock_open = self._toStr(stock_open)
        stock_max = self._toStr(stock_max)
        stock_min = self._toStr(stock_min)
        stock_close = self._toStr(stock_close)
        stock_change = self._toStr(stock_change)
        stock_change_rate = self._toStr(stock_change_rate)
        stock_volumn_hand = self._toStr(stock_volumn_hand)
        stock_volumn = self._toStr(stock_volumn)
        # print('********************',stock_name[0],stock_close[0],stock_date)

        sql = "insert into " + table + " (`name`,`date`,`open`,`max`,`min`,`close`,`change`,`change_rate`,`volumn_hand`,`volumn`) values (" + stock_name+","+stock_date+","+stock_open+","+stock_max+","+stock_min+","+stock_close+","+stock_change+","+stock_change_rate+","+stock_volumn_hand+","+stock_volumn+");"
        # print('****sql', sql)


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