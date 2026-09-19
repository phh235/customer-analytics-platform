import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"

import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"

type Row = { id: string; name: string }

const columns: CommonTableColumn<Row>[] = [
  {
    id: "name",
    header: "Tên",
    cell: (row) => row.name,
  },
]

describe("CommonTable", () => {
  it("hiển thị header, dữ liệu và summary", () => {
    render(
      <CommonTable
        data={[{ id: "1", name: "Nguyễn An" }]}
        columns={columns}
        summary="Hiển thị 1 / 1 tài khoản"
        getRowId={(row) => row.id}
      />
    )

    expect(
      screen.getByRole("columnheader", { name: "Tên" })
    ).toBeInTheDocument()
    expect(screen.getByRole("cell", { name: "Nguyễn An" })).toBeInTheDocument()
    expect(screen.getByText("Hiển thị 1 / 1 tài khoản")).toBeInTheDocument()
  })

  it("hiển thị trạng thái rỗng khi không có dữ liệu", () => {
    render(
      <CommonTable
        data={[]}
        columns={columns}
        emptyMessage="Không tìm thấy tài khoản"
      />
    )

    expect(screen.getByText("Không tìm thấy tài khoản")).toBeInTheDocument()
  })

  it("gọi callback khi chuyển trang", async () => {
    const user = userEvent.setup()
    const onPageChange = vi.fn()

    render(
      <CommonTable
        data={[{ id: "1", name: "Nguyễn An" }]}
        columns={columns}
        pagination={{
          page: 1,
          pageSize: 10,
          total: 20,
          totalPages: 2,
          hasPrevious: false,
          hasNext: true,
          onPageChange,
        }}
      />
    )

    await user.click(screen.getByRole("button", { name: "Trang sau" }))

    expect(onPageChange).toHaveBeenCalledWith(2)
  })

  it("giới hạn tối đa ba nút số trang", () => {
    render(
      <CommonTable
        data={[{ id: "1", name: "Nguyễn An" }]}
        columns={columns}
        pagination={{
          page: 5,
          pageSize: 10,
          total: 100,
          totalPages: 10,
          onPageChange: vi.fn(),
        }}
      />
    )

    expect(screen.getByText("4")).toBeInTheDocument()
    expect(screen.getByText("5")).toBeInTheDocument()
    expect(screen.getByText("6")).toBeInTheDocument()
    expect(screen.queryByText("3")).not.toBeInTheDocument()
    expect(screen.queryByText("7")).not.toBeInTheDocument()
  })
})
