# Pham vi chuc nang he thong phan tich du lieu khach hang

## 1. Ten du an

**He thong hop nhat va phan tich du lieu khach hang, ho tro du doan kha nang mua lai.**

Ten ngan gon co the dung:

**Customer Analytics & Purchase Potential Prediction System**

---

## 2. Ban chat he thong

Day la he thong **phan tich du lieu sau ban hang**, khong phai he thong ban hang.

He thong khong tao don hang, khong thanh toan, khong quan ly ton kho va khong van hanh chien dich marketing truc tiep.

He thong nhan du lieu da phat sinh tu cac nguon ben ngoai, sau do chuan hoa, phan tich, cham diem, phan khuc va du doan tiem nang mua lai cua khach hang.

Main flow:

```text
Du lieu ben ngoai
→ Import / Mapping
→ Kiem tra va lam sach
→ Hop nhat du lieu khach hang
→ Phan tich hanh vi mua
→ Phan khuc khach hang
→ Cham diem tiem nang
→ Du doan kha nang mua lai
→ Dashboard / Export
```

---

## 3. Muc tieu du an

He thong giup doanh nghiep tra loi cac cau hoi:

- Khach hang nao co gia tri cao?
- Khach hang nao co kha nang mua lai?
- Khach hang nao dang co dau hieu roi bo?
- Khach hang nao nen duoc uu tien cham soc?
- Khach hang thuong mua nhom san pham nao?
- Nhom khach hang nao nen dua vao chien dich ban hang hoac CSKH?

Ket qua cuoi cung la danh sach khach hang co insight ro rang va co the xuat ra de phuc vu hanh dong kinh doanh.

---

## 4. Nguoi dung he thong

Can phan biet ro hai khái niem:

| Doi tuong | Y nghia |
|---|---|
| Nguoi dung he thong | Admin, Analyst, Manager dang nhap de su dung he thong |
| Khach hang duoc phan tich | Ban ghi du lieu, khong dang nhap va khong thao tac trong he thong |

MVP chi can nguoi dung he thong. Khach hang cuoi khong can tai khoan.

---

## 5. Actor trong MVP

| Actor | Vai tro |
|---|---|
| ADMIN | Quan ly tai khoan, phan quyen, cau hinh va du lieu |
| ANALYST | Import du lieu, chay phan tich, xem dashboard va export ket qua |
| MANAGER | Xem dashboard, xem danh sach khach hang tiem nang va export bao cao |

Neu can rut gon MVP, co the chi dung:

```text
ADMIN
ANALYST
```

---

## 6. Nguon du lieu dau vao

Du lieu co the den tu nhieu nguon ben ngoai:

- File CSV/XLSX doanh nghiep cung cap.
- POS/cua hang.
- Website thuong mai dien tu.
- CRM/ERP.
- San thuong mai dien tu.
- He thong CSKH hoac interaction log.

Trong MVP, chi can ho tro **upload CSV/XLSX theo mau chuan**.

Chua can ket noi API truc tiep voi POS, CRM, ERP hay san thuong mai dien tu.

---

## 7. Du lieu toi thieu can co

### 7.1. Customer

- Customer ID
- Ho ten
- Email
- So dien thoai
- Gioi tinh
- Ngay sinh
- Khu vuc
- Ngay tao khach hang

### 7.2. Order / Transaction

- Order ID
- Customer ID
- Ngay giao dich
- Tong gia tri don hang
- Trang thai don hang
- Kenh ban hang

### 7.3. Order Detail

- Order ID
- Product ID
- So luong
- Don gia
- Thanh tien

### 7.4. Product

- Product ID
- Ten san pham
- Danh muc san pham
- Gia ban

### 7.5. Interaction, optional

- Customer ID
- Loai tuong tac
- Thoi gian tuong tac
- Kenh tuong tac
- Noi dung hoac metadata

Interaction la du lieu tuy chon. Neu chua co nguon interaction, MVP van phai chay duoc bang du lieu giao dich.

---

## 8. Pham vi MVP

### MVP-01. Authentication va phan quyen

Chuc nang:

- Dang nhap.
- Dang xuat.
- Quan ly tai khoan nguoi dung.
- Phan quyen ADMIN, ANALYST.
- Chan API neu nguoi dung khong co quyen.

Muc tieu:

```text
Dam bao chi nguoi co quyen moi duoc import, phan tich va xem du lieu.
```

---

### MVP-02. Import du lieu

Chuc nang:

- Upload file CSV/XLSX.
- Ho tro import Customer, Order, Order Detail va Product.
- Mapping cot trong file vao schema chuan.
- Theo doi trang thai import job.
- Luu file goc va ket qua import.

Trang thai import:

```text
PENDING
→ VALIDATING
→ PROCESSING
→ COMPLETED / PARTIALLY_COMPLETED / FAILED
```

---

### MVP-03. Kiem tra va lam sach du lieu

Chuc nang:

- Kiem tra cot bat buoc.
- Kiem tra kieu du lieu.
- Kiem tra dinh dang ngay.
- Kiem tra trung ma khach hang, trung don hang.
- Kiem tra quan he Customer - Order - Product.
- Loai hoac danh dau don hang huy/hoan.
- Luu danh sach dong loi kem ly do.

Nguyen tac:

```text
Du lieu sai phai duoc bao loi ro rang.
He thong khong tu suy dien neu thieu du lieu quan trong.
```

---

### MVP-04. Hop nhat du lieu khach hang

Chuc nang:

- Gan giao dich ve dung Customer ID.
- Chuan hoa email va so dien thoai neu co.
- Phat hien khach hang co thong tin trung lap co ban.
- Cho phep xem du lieu hop nhat theo tung khach hang.

Trong MVP, co the dung Customer ID lam khoa chinh.

Ban nang cao sau MVP moi can identity resolution phuc tap giua nhieu nguon.

---

### MVP-05. Customer 360

Chuc nang:

- Xem thong tin tong quan khach hang.
- Xem lich su giao dich.
- Tong so don hang.
- Tong gia tri da mua.
- Gia tri don hang trung binh.
- Lan mua gan nhat.
- Nhom san pham thuong mua.
- Phan khuc hien tai.
- Diem tiem nang.
- Ket qua du doan mua lai.

Muc tieu:

```text
Moi khach hang phai co mot ho so phan tich de nguoi dung hieu vi sao he thong xep hang nhu vay.
```

---

### MVP-06. Phan tich hanh vi mua hang

Chi so toi thieu:

- Recency: so ngay tu lan mua gan nhat.
- Frequency: so lan mua trong ky.
- Monetary: tong gia tri mua.
- AOV: gia tri trung binh moi don.
- Purchase Cycle: chu ky mua trung binh.
- Product Preference: nhom san pham thuong mua.
- Trend: xu huong tang, giam hoac on dinh.

Khoang thoi gian phan tich:

- 30 ngay.
- 90 ngay.
- 6 thang.
- 12 thang.
- Tuy chon.

---

### MVP-07. Phan khuc khach hang

Chuc nang:

- Tinh RFM.
- Phan khuc bang rule nghiep vu.
- Gan nhan phan khuc cho tung khach hang.
- Luu lich su thay doi phan khuc.
- Hien thi ly do khach hang thuoc phan khuc do.

Phan khuc goi y:

- Champions
- Loyal Customers
- Potential Loyalists
- New Customers
- At Risk
- Hibernating

Trong MVP, nen uu tien rule-based segmentation.

K-Means co the dua vao phase sau neu du lieu du lon va can phan cum tu dong.

---

### MVP-08. Potential Score

Chuc nang:

- Cham diem khach hang tu 0 den 100.
- Phan loai HIGH, MEDIUM, LOW.
- Hien thi cac thanh phan dong gop vao diem.
- Cho phep cau hinh trong so co ban.

Trong so mac dinh:

| Thanh phan | Trong so |
|---|---:|
| Recency | 30% |
| Frequency | 25% |
| Monetary | 20% |
| Interaction | 15% |
| Trend | 10% |

Neu khong co Interaction, can phan bo lai trong so cho cac thanh phan con lai.

Muc diem:

| Muc | Diem |
|---|---:|
| HIGH | 80 - 100 |
| MEDIUM | 50 - 79 |
| LOW | 0 - 49 |

Luu y:

```text
Potential Score la diem nghiep vu theo rule.
No khong dong nghia voi xac suat mua hang cua model ML.
```

---

### MVP-09. Du doan kha nang mua lai

Chuc nang:

- Du doan khach hang co kha nang phat sinh giao dich trong 90 ngay toi hay khong.
- Luu xac suat mua lai.
- Luu model version.
- Luu ngay du doan.
- Luu prediction horizon.
- Luu feature window.

Output vi du:

```json
{
  "customer_id": "C001",
  "prediction_date": "2026-08-11",
  "prediction_horizon_days": 90,
  "purchase_probability": 0.76,
  "model_version": "v1.0"
}
```

Nguyen tac bat buoc:

```text
Feature window va prediction window khong duoc chong lan.
Khong duoc dua du lieu tuong lai vao feature.
```

ML co the de sau cac module import, data quality, RFM va Potential Score.

---

### MVP-10. Dashboard va export

Dashboard toi thieu:

- Tong so khach hang.
- Tong doanh thu.
- So don hang.
- AOV.
- Phan bo phan khuc.
- Top khach hang tiem nang.
- Top khach hang co nguy co roi bo.
- Phan bo muc HIGH, MEDIUM, LOW.
- Nhom san pham duoc quan tam nhieu.

Bo loc:

- Thoi gian.
- Phan khuc.
- Muc tiem nang.
- Nhom san pham.
- Kenh ban hang.

Export:

- CSV.
- XLSX.
- Danh sach khach hang muc tieu.
- Ket qua phan khuc.
- Ket qua du doan.

---

## 9. Ngoai pham vi MVP

Khong lam trong MVP:

- Gio hang.
- Dat hang.
- Thanh toan.
- Hoa don.
- Van chuyen.
- Quan ly ton kho.
- Quan ly khuyen mai.
- Website ban hang cho khach cuoi.
- CRM sales pipeline.
- Ticket CSKH day du.
- Tu dong gui email/SMS.
- Tu dong chay chien dich marketing.
- Ket noi API truc tiep voi nhieu he thong ben ngoai.
- Dong bo realtime.
- Model ML nang cao.
- K-Means neu du lieu chua du lon.

Nguyen tac:

```text
He thong chi phan tich va de xuat.
He thong khong thuc hien ban hang thay cac he thong ben ngoai.
```

---

## 10. Ranh gioi voi he thong ben ngoai

| He thong ben ngoai lam | He thong nay lam |
|---|---|
| Tao don hang | Nhan du lieu don hang |
| Thu tien | Phan tich gia tri giao dich |
| Quan ly san pham | Phan tich nhom san pham |
| Quan ly ton kho | Khong nam trong pham vi |
| Chay chien dich marketing | De xuat danh sach khach hang muc tieu |
| Gui email/SMS | Export danh sach de he thong khac xu ly |
| Luu du lieu goc | Chuan hoa va tao insight |

---

## 11. Thu tu trien khai de xuat

```text
1. Foundation + Authentication
2. Import CSV/XLSX
3. Data Quality
4. Customer 360
5. RFM Analysis
6. Rule-based Segmentation
7. Potential Score
8. Dashboard + Export
9. ML Prediction v1
10. Multi-source Integration, sau MVP
```

---

## 12. Definition of Done cho MVP

MVP duoc xem la hoan thanh khi:

- ADMIN va ANALYST dang nhap duoc.
- ANALYST upload duoc file du lieu.
- He thong kiem tra du lieu va bao dong loi ro rang.
- Du lieu hop le duoc luu vao database.
- Moi khach hang co Customer 360.
- He thong tinh duoc RFM.
- He thong gan duoc phan khuc.
- He thong tinh duoc Potential Score.
- Dashboard hien thi duoc insight co ban.
- Nguoi dung export duoc danh sach khach hang muc tieu.
- ML v1 du doan duoc kha nang mua lai trong 90 ngay hoac co baseline ro rang neu chua du du lieu.

---

## 13. Tom tat pham vi chot

Du an nay khong phai la he thong ban hang.

Du an nay la:

```text
He thong nhan du lieu ban hang tu ben ngoai,
chuan hoa du lieu,
phan tich khach hang,
phan khuc,
cham diem tiem nang,
du doan kha nang mua lai,
va xuat insight phuc vu kinh doanh.
```

Phien ban MVP nen tap trung vao:

```text
Import du lieu
→ Lam sach
→ Customer 360
→ RFM
→ Segment
→ Potential Score
→ Dashboard
→ Export
```

ML va ket noi da nguon nen lam sau khi nen du lieu da on dinh.
