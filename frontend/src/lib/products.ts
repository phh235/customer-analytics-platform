export type Product = {
  id: string
  name: string
  category: string
  price: number
  shortDescription: string
  description: string
  image: string
}

export const products: Product[] = [
  {
    id: "urban-run",
    name: "Giày thể thao Urban Run",
    category: "Giày dép",
    price: 1290000,
    shortDescription: "Thiết kế nhẹ, phù hợp cho những buổi chạy hằng ngày.",
    description:
      "Urban Run mang đến cảm giác thoải mái và linh hoạt trong từng bước chạy. Đôi giày có đệm êm, kiểu dáng hiện đại và dễ phối với trang phục hằng ngày.",
    image:
      "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "classic-watch",
    name: "Đồng hồ Classic",
    category: "Phụ kiện thời trang",
    price: 2490000,
    shortDescription: "Phong cách tối giản, thanh lịch cho mọi dịp.",
    description:
      "Classic is mẫu đồng hồ dành cho người yêu thích sự tinh tế. Mặt số dễ đọc, dây đeo bền đẹp và thiết kế tối giản giúp bạn sử dụng linh hoạt mỗi ngày.",
    image:
      "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "wave-pro",
    name: "Tai nghe Wave Pro",
    category: "Thiết bị âm thanh",
    price: 1890000,
    shortDescription: "Âm thanh rõ nét cùng trải nghiệm nghe thoải mái.",
    description:
      "Wave Pro được thiết kế cho những giờ làm việc, học tập và giải trí tập trung. Sản phẩm cho âm thanh cân bằng, đeo êm tai và dễ dàng kết nối.",
    image:
      "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "urban-explorer",
    name: "Balo Urban Explorer",
    category: "Túi & ba lô",
    price: 1150000,
    shortDescription:
      "Balo chống nước thời trang, tiện lợi với nhiều ngăn chứa.",
    description:
      "Với chất liệu chống thấm nước cao cấp cùng thiết kế công học phân bổ trọng lượng thông minh, Balo Urban Explorer đồng hành cùng bạn trên mọi hành trình đô thị thường nhật.",
    image:
      "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "nomad-tumbler",
    name: "Bình giữ nhiệt Nomad",
    category: "Đồ gia dụng",
    price: 450000,
    shortDescription: "Giữ nhiệt nóng/lạnh vượt trội, chất liệu thép không gỉ.",
    description:
      "Bình giữ nhiệt Nomad giúp bạn thưởng thức đồ uống yêu thích ở nhiệt độ hoàn hảo suốt cả ngày dài. Nắp đậy chống rò rỉ tuyệt đối cùng quai xách tiện dụng.",
    image:
      "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "aura-lamp",
    name: "Đèn bàn Aura",
    category: "Đồ gia dụng",
    price: 890000,
    shortDescription: "Đèn LED bảo vệ mắt, thiết kế tối giản xoay linh hoạt.",
    description:
      "Chiếu sáng không gian làm việc của bạn với ánh sáng tự nhiên không nhấp nháy từ Đèn bàn Aura. Ba chế độ nhiệt độ màu cùng núm vặn điều chỉnh độ sáng trực quan.",
    image:
      "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "heritage-notebook",
    name: "Sổ tay da Heritage",
    category: "Văn phòng phẩm",
    price: 320000,
    shortDescription: "Bìa da bò thật nhập khẩu, giấy viết chống lem nhòe.",
    description:
      "Mỗi cuốn sổ tay da Heritage được chế tác thủ công tỉ mỉ với ruột giấy chống lóa thân thiện với mắt, mang lại cảm hứng sáng tạo và ghi chép bất tận.",
    image:
      "https://images.unsplash.com/photo-1531346878377-a5be20888e57?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "bloom-speaker",
    name: "Loa di động Bloom",
    category: "Thiết bị âm thanh",
    price: 1590000,
    shortDescription: "Âm thanh vòm sống động, chống nước chuẩn IPX7.",
    description:
      "Tận hưởng âm nhạc chất lượng cao mọi lúc mọi nơi với loa Bloom. Thời lượng pin cực khủng lên đến 15 giờ liên tục và kết nối Bluetooth 5.3 nhanh chóng ổn định.",
    image:
      "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "apex-keyboard",
    name: "Bàn phím cơ Apex",
    category: "Thiết bị công nghệ",
    price: 2290000,
    shortDescription: "Bàn phím cơ không dây, switch êm ái, đèn nền RGB.",
    description:
      "Bàn phím cơ không dây Apex với switch cơ học cao cấp mang lại trải nghiệm gõ phím mượt mà và yên tĩnh. Thiết kế công thái học cùng thời lượng pin sử dụng lên đến cả tuần.",
    image:
      "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "zen-mouse",
    name: "Chuột không dây Zen",
    category: "Thiết bị công nghệ",
    price: 950000,
    shortDescription: "Chuột không dây công thái học, cảm biến cực nhạy.",
    description:
      "Zen Mouse sở hữu thiết kế công thái học giúp ôm sát lòng bàn tay, giảm thiểu mỏi cổ tay khi làm việc lâu. Kết nối bluetooth thông minh và pin sạc Type-C tiện lợi.",
    image:
      "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "focus-planner",
    name: "Sổ tay lập kế hoạch Focus",
    category: "Văn phòng phẩm",
    price: 250000,
    shortDescription: "Thiết kế khoa học giúp quản lý mục tiêu hiệu quả.",
    description:
      "Sổ tay Focus Planner giúp bạn tối ưu hóa thời gian và theo dõi mục tiêu cá nhân hằng ngày. Chất liệu giấy cao cấp chống nhòe và bố cục ghi chép thông minh.",
    image:
      "https://images.unsplash.com/photo-1517842645767-c639042777db?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "polar-glasses",
    name: "Kính râm Polar",
    category: "Phụ kiện thời trang",
    price: 1350000,
    shortDescription: "Tròng kính phân cực chống tia UV vượt trội.",
    description:
      "Kính râm Polar không chỉ bảo vệ đôi mắt của bạn khỏi tia cực tím mà còn tăng cường độ rõ nét khi di chuyển ngoài trời. Gọng kính siêu nhẹ, bền bỉ và thời trang.",
    image:
      "https://images.unsplash.com/photo-1572635196237-14b3f281503f?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "solace-backpack",
    name: "Balo tối giản Solace",
    category: "Túi & ba lô",
    price: 1490000,
    shortDescription: "Phong cách thanh lịch, ngăn chứa laptop chống sốc dày.",
    description:
      "Balo Solace kết hợp giữa sự thanh lịch tối giản và tính năng ưu việt. Ngăn chống sốc chuyên dụng bảo vệ máy tính của bạn tối đa, phù hợp cho đi làm và đi học.",
    image:
      "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "stellar-thermos",
    name: "Ly giữ nhiệt Stellar",
    category: "Đồ gia dụng",
    price: 520000,
    shortDescription:
      "Ly giữ nhiệt thép không gỉ 2 lớp, đi kèm ống hút tiện lợi.",
    description:
      "Stellar Thermos giữ nhiệt đồ uống nóng hoặc lạnh hoàn hảo trong nhiều giờ. Thiết kế trẻ trung, lớp phủ nhám chống trầy xước và nắp chống tràn cực tốt.",
    image:
      "https://images.unsplash.com/photo-1577937927133-66ef06acdf18?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "echo-buds",
    name: "Tai nghe không dây Echo",
    category: "Thiết bị âm thanh",
    price: 1250000,
    shortDescription: "Tai nghe true wireless âm bass sâu, chống ồn chủ động.",
    description:
      "Trải nghiệm âm thanh đắm chìm với Tai nghe Echo Buds. Công nghệ chống ồn chủ động (ANC) giúp lọc sạch tạp âm xung quanh, mang đến không gian âm nhạc trọn vẹn.",
    image:
      "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "amber-perfume",
    name: "Nước hoa Amber Woods",
    category: "Làm đẹp",
    price: 1950000,
    shortDescription: "Hương thơm gỗ ấm áp, sang trọng và lưu hương lâu.",
    description:
      "Nước hoa Amber Woods mở ra với hương cam bergamot tươi mát, hòa quyện cùng nốt hương gỗ tuyết tùng và hổ phách ấm áp đầy cuốn hút. Sự lựa chọn hoàn hảo cho các buổi tối sang trọng.",
    image:
      "https://images.unsplash.com/photo-1541643600914-78b084683601?auto=format&fit=crop&w=900&q=80",
  },
]

export const productPriceFormatter = new Intl.NumberFormat("vi-VN", {
  style: "currency",
  currency: "VND",
  maximumFractionDigits: 0,
})

export const normalizeProductText = (value: string) =>
  value.toLocaleLowerCase("vi-VN")

export function getProductById(productId: string) {
  return products.find((product) => product.id === productId)
}
