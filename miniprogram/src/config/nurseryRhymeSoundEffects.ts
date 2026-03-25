import type { GroupedOptions } from './nurseryRhymeConfig'

export const SOUND_EFFECTS: GroupedOptions[] = [
  {
    group: '动物声',
    icon: '🐾',
    options: [
      { value: 'dog', label: '小狗汪汪' },
      { value: 'cat', label: '小猫喵喵' },
      { value: 'bird', label: '小鸟叽叽' },
      { value: 'lion', label: '狮子吼' },
      { value: 'frog', label: '青蛙呱呱' },
      { value: 'chicken', label: '小鸡叽叽' },
      { value: 'cow', label: '牛哞哞' },
      { value: 'sheep', label: '羊咩咩' },
      { value: 'horse', label: '马嘶鸣' },
      { value: 'elephant', label: '大象叫' }
    ]
  },
  {
    group: '自然声',
    icon: '🌿',
    options: [
      { value: 'rain', label: '下雨' },
      { value: 'water', label: '流水' },
      { value: 'wind', label: '风声' },
      { value: 'thunder', label: '雷声' },
      { value: 'waves', label: '海浪' },
      { value: 'birds_chirping', label: '鸟鸣' },
      { value: 'insects', label: '虫鸣' },
      { value: 'leaves', label: '落叶沙沙' },
      { value: 'waterfall', label: '瀑布' },
      { value: 'campfire', label: '篝火' }
    ]
  },
  {
    group: '趣味声',
    icon: '😄',
    options: [
      { value: 'laugh', label: '笑声' },
      { value: 'cheer', label: '欢呼' },
      { value: 'balloon', label: '气球' },
      { value: 'boing', label: '弹簧跳跃' },
      { value: 'slip', label: '滑稽摔倒' },
      { value: 'sneeze', label: '打喷嚏' },
      { value: 'hiccup', label: '打嗝' },
      { value: 'whistle', label: '吹口哨' },
      { value: 'kiss', label: '亲吻' },
      { value: 'clap', label: '拍手' }
    ]
  },
  {
    group: '交通声',
    icon: '🚗',
    options: [
      { value: 'car_horn', label: '汽车喇叭' },
      { value: 'train', label: '火车汽笛' },
      { value: 'airplane', label: '飞机起飞' },
      { value: 'ship', label: '轮船鸣笛' },
      { value: 'bicycle', label: '自行车铃' },
      { value: 'subway', label: '地铁报站' }
    ]
  },
  {
    group: '生活声',
    icon: '🏠',
    options: [
      { value: 'doorbell', label: '门铃' },
      { value: 'alarm', label: '闹钟' },
      { value: 'cooking', label: '厨房烹饪' },
      { value: 'knock', label: '敲门' },
      { value: 'phone', label: '电话铃' },
      { value: 'door', label: '开门关门' },
      { value: 'footsteps', label: '脚步声' },
      { value: 'page_flip', label: '翻书' }
    ]
  },
  {
    group: '节日声',
    icon: '🎉',
    options: [
      { value: 'fireworks', label: '烟花' },
      { value: 'firecrackers', label: '鞭炮' },
      { value: 'jingle', label: '圣诞铃铛' },
      { value: 'party_horn', label: '派对喇叭' },
      { value: 'candle_blow', label: '生日吹蜡烛' },
      { value: 'unwrap', label: '礼物拆封' }
    ]
  },
  {
    group: '科幻声',
    icon: '🚀',
    options: [
      { value: 'robot', label: '机器人' },
      { value: 'spaceship', label: '太空飞船' },
      { value: 'laser', label: '激光' },
      { value: 'beep', label: '电子滴答' },
      { value: 'portal', label: '传送门' },
      { value: 'tech', label: '未来科技' }
    ]
  },
  {
    group: '奇幻声',
    icon: '🧙',
    options: [
      { value: 'magic', label: '魔法施放' },
      { value: 'fairy', label: '精灵飞舞' },
      { value: 'castle', label: '城堡大门' },
      { value: 'dragon', label: '龙吟' },
      { value: 'wand', label: '魔杖挥动' },
      { value: 'treasure', label: '宝箱开启' }
    ]
  },
  {
    group: '游戏声',
    icon: '🎮',
    options: [
      { value: 'level_up', label: '升级' },
      { value: 'coin', label: '金币' },
      { value: 'victory', label: '胜利' },
      { value: 'jump', label: '跳跃' },
      { value: 'power_up', label: '道具获得' },
      { value: 'complete', label: '任务完成' }
    ]
  }
] as const
