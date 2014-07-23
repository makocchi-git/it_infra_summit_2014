README
======

template を使う前にいくつか必要な作業があります


値のマッピングの追加
--------------------

* template 内で値のマッピングを使っています
* 「管理」「一般設定」「値のマッピング」で作成してください

```
Cisco Fan Status
1 ⇒ normal
2 ⇒ warning
3 ⇒ critical
4 ⇒ shutdown
5 ⇒ notPresent
6 ⇒ notFunctioning
  
Brocade Sensor Status
1 ⇒ unknown
2 ⇒ faulty
3 ⇒ below-min
4 ⇒ nominal
5 ⇒ above-max
6 ⇒ absent
  
Cisco Power Supply Status
1 ⇒ normal
2 ⇒ warning
3 ⇒ critical
4 ⇒ shutdown
5 ⇒ notPresent
6 ⇒ notFunctioning
  
Cisco Temperature Status
1 ⇒ normal
2 ⇒ warning
3 ⇒ critical
4 ⇒ shutdown
5 ⇒ notPresent
6 ⇒ notFunctioning
  
NW General Status
1 ⇒ UP
2 ⇒ DOWN
```

ディスカバリルールの作成
------------------------

* 例として NW-CiscoSW というルールを作ってみます

![](https://github.com/makocchi-git/it_infra_summit_2014/blob/master/Network/screenshots/discovery.png)


アクションの作成
----------------

* 上記で作った NW-CiscoSW を使ってアクションを作成してください

![](https://github.com/makocchi-git/it_infra_summit_2014/blob/master/Network/screenshots/action1.png)

![](https://github.com/makocchi-git/it_infra_summit_2014/blob/master/Network/screenshots/action2.png)


snmptt.conf
-----------

* snmptt.conf を適宜設定してください
* sample として [snmptt_sample.conf](https://github.com/makocchi-git/it_infra_summit_2014/blob/master/Network/snmptt_sample.conf) を置いておきます
