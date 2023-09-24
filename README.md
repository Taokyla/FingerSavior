# 谁来拯救你，我的手指 (Finger Savior)

---

### 最终目录

```
FingerSavior
├─lib
|  └─*.py...
├─main.py
├─模块文件夹
|     ├─name1@command.arg1.arg2.png
|     ├─name2.offsetx.offsety.png
|     └─name3.topleftx.toplefty.bottomrightx.bottomrighty.png
```

### command列表

- **offset** : 点击偏移, 参数dx, dy. `name@offset.dx.dy.png`等效于`name2.dx.dy.png`
- **redirect** : 重定向, 参数pos1x, pos1y, pos2x, pos2y. 同样效果`name3.topleftx.toplefty.bottomrightx.bottomrighty.png`
- **goto** ：指定执行, 参数name. 立即结束本次flow循环，并指定下次循环为`name`
- **save** : 保存当前截图，不做任何处理，flow循环继续
- **exit** : 关闭脚本
- **skip** : 跳过当前flow, ~~不知道有什么意义~~
- **delay** : 额外延迟, 参数second, 或者两个参数, 用randint
- **jump** : 跳转到, 参数name, 跳转到本次flow循环后续flow的的某个, 不会结束循环, 只能跳转到排序在其后的flow
- **count** : 累计, 参数count,累计点击到`count`次时关闭脚本
- **uselastclick** : 使用上一个flow的点击位置, 模拟玩家鼠标没有移动一直点


### future

- 单个图片多个command