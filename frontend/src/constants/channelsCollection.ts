interface Channel {
  id: number;
  name: string;
  subscribers: number;
  category: string;
  verified: boolean;
  country: string;
  imageUrl: string;
}

const channels: Channel[] = [
  {
    id: 1,
    name: 'Telegram premium',
    subscribers: 8550929,
    category: 'Новости и СМИ',
    verified: true,
    country: 'Россия',
    imageUrl:
      'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCTMa_qVsdRAVRTLr3wiQf_S6sun9vF0ZskHLNVcicDvbx4PijZTLnrxWgxxzolar0iT0&usqp=CAU',
  },
  {
    id: 2,
    name: 'РИА Новости',
    subscribers: 3337342,
    category: 'Новости и СМИ',
    verified: true,
    country: 'Россия',
    imageUrl:
      'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCTMa_qVsdRAVRTLr3wiQf_S6sun9vF0ZskHLNVcicDvbx4PijZTLnrxWgxxzolar0iT0&usqp=CAU',
  },
  {
    id: 3,
    name: 'Банкста',
    subscribers: 413246,
    category: 'Экономика',
    verified: false,
    country: 'Казахстан',
    imageUrl:
      'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCTMa_qVsdRAVRTLr3wiQf_S6sun9vF0ZskHLNVcicDvbx4PijZTLnrxWgxxzolar0iT0&usqp=CAU',
  },
  {
    id: 4,
    name: 'Экономика',
    subscribers: 184902,
    category: 'Экономика',
    verified: true,
    country: 'Россия',
    imageUrl:
      'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCTMa_qVsdRAVRTLr3wiQf_S6sun9vF0ZskHLNVcicDvbx4PijZTLnrxWgxxzolar0iT0&usqp=CAU',
  },
  {
    id: 5,
    name: 'Дмитрий Медведев',
    subscribers: 8550929,
    category: 'Политика',
    verified: true,
    country: 'Россия',
    imageUrl:
      'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCTMa_qVsdRAVRTLr3wiQf_S6sun9vF0ZskHLNVcicDvbx4PijZTLnrxWgxxzolar0iT0&usqp=CAU',
  },
  {
    id: 6,
    name: 'Top series',
    subscribers: 3337342,
    category: 'Видео и фильмы',
    verified: true,
    country: 'Россия',
    imageUrl:
      'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCTMa_qVsdRAVRTLr3wiQf_S6sun9vF0ZskHLNVcicDvbx4PijZTLnrxWgxxzolar0iT0&usqp=CAU',
  },
  {
    id: 7,
    name: 'Банкста',
    subscribers: 413246,
    category: 'Экономика',
    verified: false,
    country: 'Казахстан',
    imageUrl:
      'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCTMa_qVsdRAVRTLr3wiQf_S6sun9vF0ZskHLNVcicDvbx4PijZTLnrxWgxxzolar0iT0&usqp=CAU',
  },
  {
    id: 8,
    name: 'True crimes',
    subscribers: 184902,
    category: 'Видео и фильмы',
    verified: true,
    country: 'Россия',
    imageUrl:
      'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCTMa_qVsdRAVRTLr3wiQf_S6sun9vF0ZskHLNVcicDvbx4PijZTLnrxWgxxzolar0iT0&usqp=CAU',
  },
  {
    id: 9,
    name: 'Аналитика',
    subscribers: 8550929,
    category: 'Финансы',
    verified: true,
    country: 'Россия',
    imageUrl:
      'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCTMa_qVsdRAVRTLr3wiQf_S6sun9vF0ZskHLNVcicDvbx4PijZTLnrxWgxxzolar0iT0&usqp=CAU',
  },
  {
    id: 10,
    name: 'Вячеслав Володин',
    subscribers: 3337342,
    category: 'Политика',
    verified: true,
    country: 'Россия',
    imageUrl:
      'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCTMa_qVsdRAVRTLr3wiQf_S6sun9vF0ZskHLNVcicDvbx4PijZTLnrxWgxxzolar0iT0&usqp=CAU',
  },
  {
    id: 11,
    name: 'Pictures',
    subscribers: 413246,
    category: 'Картинки и фото',
    verified: true,
    country: 'Казахстан',
    imageUrl:
      'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCTMa_qVsdRAVRTLr3wiQf_S6sun9vF0ZskHLNVcicDvbx4PijZTLnrxWgxxzolar0iT0&usqp=CAU',
  },
  {
    id: 12,
    name: 'Экономика education',
    subscribers: 184902,
    category: 'Экономика',
    verified: true,
    country: 'Россия',
    imageUrl:
      'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCTMa_qVsdRAVRTLr3wiQf_S6sun9vF0ZskHLNVcicDvbx4PijZTLnrxWgxxzolar0iT0&usqp=CAU',
  },
  {
    id: 13,
    name: 'ТАСС',
    subscribers: 8550929,
    category: 'Новости и СМИ',
    verified: true,
    country: 'Россия',
    imageUrl:
      'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCTMa_qVsdRAVRTLr3wiQf_S6sun9vF0ZskHLNVcicDvbx4PijZTLnrxWgxxzolar0iT0&usqp=CAU',
  },
  {
    id: 14,
    name: 'Доктор Комаровский',
    subscribers: 3337342,
    category: 'Здоровье',
    verified: false,
    country: 'Украина',
    imageUrl:
      'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCTMa_qVsdRAVRTLr3wiQf_S6sun9vF0ZskHLNVcicDvbx4PijZTLnrxWgxxzolar0iT0&usqp=CAU',
  },
  {
    id: 15,
    name: 'Easy English',
    subscribers: 413246,
    category: 'Лингвистика',
    verified: false,
    country: 'Беларусь',
    imageUrl:
      'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCTMa_qVsdRAVRTLr3wiQf_S6sun9vF0ZskHLNVcicDvbx4PijZTLnrxWgxxzolar0iT0&usqp=CAU',
  },
  {
    id: 16,
    name: 'Экономика',
    subscribers: 184902,
    category: 'Технологии',
    verified: true,
    country: 'Россия',
    imageUrl:
      'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCTMa_qVsdRAVRTLr3wiQf_S6sun9vF0ZskHLNVcicDvbx4PijZTLnrxWgxxzolar0iT0&usqp=CAU',
  },
  {
    id: 17,
    name: 'Новости Россия',
    subscribers: 184902,
    category: 'Новости и СМИ',
    verified: true,
    country: 'Россия',
    imageUrl:
      'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCTMa_qVsdRAVRTLr3wiQf_S6sun9vF0ZskHLNVcicDvbx4PijZTLnrxWgxxzolar0iT0&usqp=CAU',
  },
];

export default channels;
