# Dazhong_Spider
大众点评搜索接口列表页采集 店铺详情页店铺信息及店铺评论数据采集

  破解大众店铺列表页 字体文件反爬(使用redis存储字体库)  
  破解大众店铺详情页 svg映射反爬  
  集成代理池 多线程(一个线程对应一个账号cookie)  
  大规模爬取需要自行扩展

## 结构  
  1.Font_decryption.py 列表页字体库解析模块  
  2.Font_svg.py 详情页svg文字映射解析模块  
  3.ip_poll 代理池  
  4.list_page_req.py 列表页请求模块  
  5.mysql_model.py mysql增删改查封装  
  6.save_fontlist.py 文字映射表 写死  
  7.spider_main.py 详情页请求模块  
  
  
## 配置  
 1.配置 ip_poll 代理池api (原项目用熊猫代理)  
 2.配置spider_main.py 与 list_page_req.py 账号cookie cookie数量与线程数量对应  
 3.配置mysql_model mysql信息  

