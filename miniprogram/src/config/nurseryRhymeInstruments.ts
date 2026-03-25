import type { GroupedOptions } from './nurseryRhymeConfig'

// 乐器（按家族分组）
export const INSTRUMENTS_BY_FAMILY: GroupedOptions[] = [
  {
    group: '键盘类',
    icon: '🎹',
    options: [
      { value: 'piano', label: '钢琴' },
      { value: 'electric_piano', label: '电钢琴' },
      { value: 'organ', label: '风琴' },
      { value: 'accordion', label: '手风琴' },
      { value: 'synth', label: '合成器' },
      { value: 'rhodes', label: 'Rhodes' },
      { value: 'toy_piano', label: '玩具钢琴' }
    ]
  },
  {
    group: '弦乐类',
    icon: '🎸',
    options: [
      { value: 'guitar', label: '吉他' },
      { value: 'ukulele', label: '尤克里里' },
      { value: 'violin', label: '小提琴' },
      { value: 'cello', label: '大提琴' },
      { value: 'harp', label: '竖琴' },
      { value: 'bass', label: '贝斯' },
      { value: 'mandolin', label: '曼陀林' }
    ]
  },
  {
    group: '管乐类',
    icon: '🎺',
    options: [
      { value: 'flute', label: '长笛' },
      { value: 'saxophone', label: '萨克斯' },
      { value: 'trumpet', label: '小号' },
      { value: 'clarinet', label: '单簧管' },
      { value: 'harmonica', label: '口琴' },
      { value: 'recorder', label: '竖笛' },
      { value: 'piccolo', label: '短笛' }
    ]
  },
  {
    group: '打击类',
    icon: '🥁',
    options: [
      { value: 'drums', label: '架子鼓' },
      { value: 'xylophone', label: '木琴' },
      { value: 'glockenspiel', label: '铁琴' },
      { value: 'triangle', label: '三角铁' },
      { value: 'shaker', label: '沙锤' },
      { value: 'tambourine', label: '铃鼓' },
      { value: 'bongo', label: '手鼓' },
      { value: 'cajon', label: '卡宏鼓' }
    ]
  },
  {
    group: '电子类',
    icon: '🎛️',
    options: [
      { value: 'synth_pad', label: '合成器Pad' },
      { value: 'drum_machine', label: '电子鼓' },
      { value: '808', label: '808' },
      { value: 'sampler', label: '采样器' },
      { value: 'sequencer', label: '音序器' }
    ]
  },
  {
    group: '民族类',
    icon: '🪕',
    options: [
      { value: 'guzheng', label: '古筝' },
      { value: 'erhu', label: '二胡' },
      { value: 'pipa', label: '琵琶' },
      { value: 'dizi', label: '笛子' },
      { value: 'suona', label: '唢呐' },
      { value: 'african_drum', label: '非洲鼓' },
      { value: 'steel_drum', label: '钢鼓' }
    ]
  }
] as const

// 乐器（按氛围分组）
export const INSTRUMENTS_BY_MOOD: GroupedOptions[] = [
  {
    group: '温暖柔和',
    options: [
      { value: 'piano', label: '钢琴' },
      { value: 'guitar', label: '吉他' },
      { value: 'harp', label: '竖琴' },
      { value: 'strings', label: '弦乐' }
    ]
  },
  {
    group: '活泼欢快',
    options: [
      { value: 'xylophone', label: '木琴' },
      { value: 'tambourine', label: '铃鼓' },
      { value: 'ukulele', label: '尤克里里' },
      { value: 'bongo', label: '手鼓' }
    ]
  },
  {
    group: '现代电子',
    options: [
      { value: 'synth', label: '合成器' },
      { value: 'drum_machine', label: '电子鼓' },
      { value: '808', label: '808' }
    ]
  },
  {
    group: '民族特色',
    options: [
      { value: 'guzheng', label: '古筝' },
      { value: 'dizi', label: '笛子' },
      { value: 'african_drum', label: '非洲鼓' }
    ]
  },
  {
    group: '爵士风情',
    options: [
      { value: 'saxophone', label: '萨克斯' },
      { value: 'piano', label: '钢琴' },
      { value: 'bass', label: '贝斯' },
      { value: 'drums', label: '架子鼓' }
    ]
  }
] as const
