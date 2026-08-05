export type Product = {
  id: string
  name: string
  price: number
  shortDescription: string
  description: string
  image: string
}

export const products: Product[] = [
  {
    id: "urban-run",
    name: "Giày thể thao Urban Run",
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
    price: 1150000,
    shortDescription: "Balo chống nước thời trang, tiện lợi với nhiều ngăn chứa.",
    description:
      "Với chất liệu chống thấm nước cao cấp cùng thiết kế công học phân bổ trọng lượng thông minh, Balo Urban Explorer đồng hành cùng bạn trên mọi hành trình đô thị thường nhật.",
    image:
      "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "nomad-tumbler",
    name: "Bình giữ nhiệt Nomad",
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
    price: 1590000,
    shortDescription: "Âm thanh vòm sống động, chống nước chuẩn IPX7.",
    description:
      "Tận hưởng âm nhạc chất lượng cao mọi lúc mọi nơi với loa Bloom. Thời lượng pin cực khủng lên đến 15 giờ liên tục và kết nối Bluetooth 5.3 nhanh chóng ổn định.",
    image:
      "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=900&q=80",
  },
]

export const productPriceFormatter = new Intl.NumberFormat("vi-VN", {
  style: "currency",
  currency: "VND",
  maximumFractionDigits: 0,
})

export function getProductById(productId: string) {
  return products.find((product) => product.id === productId)
}
