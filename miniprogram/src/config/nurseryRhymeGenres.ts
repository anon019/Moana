import type { GroupedOptions } from './nurseryRhymeConfig'

// 音乐流派（分组）
export const MUSIC_GENRES: GroupedOptions[] = [
  {
    group: '儿童专属',
    options: [
      { value: 'children', label: '儿歌' },
      { value: 'nursery', label: '童谣' },
      { value: 'lullaby', label: '摇篮曲' },
      { value: 'educational', label: '教育歌曲' },
      { value: 'animation', label: '动画原声' }
    ]
  },
  {
    group: '流行现代',
    options: [
      { value: 'pop', label: '流行' },
      { value: 'edm', label: '电子舞曲' },
      { value: 'synth_pop', label: 'Synth-Pop' },
      { value: 'kpop', label: 'K-Pop' },
      { value: 'jpop', label: 'J-Pop' },
      { value: 'cpop', label: '华语流行' }
    ]
  },
  {
    group: '民谣原声',
    options: [
      { value: 'folk', label: '民谣' },
      { value: 'country', label: '乡村' },
      { value: 'acoustic', label: 'Acoustic' },
      { value: 'indie_folk', label: '独立民谣' },
      { value: 'world', label: '世界音乐' }
    ]
  },
  {
    group: '古典优雅',
    options: [
      { value: 'classical', label: '古典改编' },
      { value: 'orchestral', label: '交响乐' },
      { value: 'chamber', label: '室内乐' },
      { value: 'opera', label: '歌剧改编' },
      { value: 'neoclassical', label: '新古典' }
    ]
  },
  {
    group: '爵士蓝调',
    options: [
      { value: 'jazz', label: '爵士' },
      { value: 'blues', label: '布鲁斯' },
      { value: 'bossa_nova', label: 'Bossa Nova' },
      { value: 'swing', label: 'Swing' },
      { value: 'funk', label: '放克' }
    ]
  },
  {
    group: '节奏韵律',
    options: [
      { value: 'hiphop', label: '嘻哈' },
      { value: 'rap', label: '说唱' },
      { value: 'rnb', label: 'R&B' },
      { value: 'reggae', label: '雷鬼' },
      { value: 'latin', label: '拉丁' }
    ]
  },
  {
    group: '电子实验',
    options: [
      { value: 'ambient', label: 'Ambient' },
      { value: 'lofi', label: 'Lo-fi' },
      { value: 'chillhop', label: 'Chillhop' },
      { value: 'electronic', label: '电子' },
      { value: 'house', label: 'House' },
      { value: 'trance', label: 'Trance' }
    ]
  },
  {
    group: '摇滚另类',
    options: [
      { value: 'rock', label: '摇滚' },
      { value: 'indie_rock', label: '独立摇滚' },
      { value: 'punk', label: '朋克' },
      { value: 'alternative', label: '另类' }
    ]
  },
  {
    group: '特殊风格',
    options: [
      { value: 'game', label: '游戏音乐' },
      { value: 'cinematic', label: '电影配乐' },
      { value: 'new_age', label: 'New Age' },
      { value: 'acapella', label: 'A Cappella' },
      { value: 'gospel', label: 'Gospel' }
    ]
  }
] as const
