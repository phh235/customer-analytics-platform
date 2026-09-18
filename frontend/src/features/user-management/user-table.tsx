import { useMemo } from "react"
import { EditIcon, Trash2Icon } from "lucide-react"

import { EmptyTableState } from "@/components/admin/management/empty-table-state"
import { AppDropdown } from "@/components/common/app-dropdown"
import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { UserAvatar } from "@/components/common/user-avatar"
import { Badge } from "@/components/ui/badge"
import {
  USER_ROLE_LABELS,
  type User,
  type UserRole,
  type UserStatus,
} from "@/types/user"
import type { PaginatedUsersResponse } from "@/types/user-management"

const roleLabel = (role: UserRole) => USER_ROLE_LABELS[role]

function UserStatusBadge({ status }: { status: UserStatus }) {
  const content = {
    ACTIVE: { label: "Đang hoạt động", variant: "success" as const },
    DISABLED: { label: "Đã vô hiệu hóa", variant: "destructive" as const },
    LOCKED: { label: "Đang bị khóa", variant: "warning" as const },
  }[status]

  return <Badge variant={content.variant}>{content.label}</Badge>
}

const formatUserDate = (value: string | null) => {
  if (!value) return "Chưa đăng nhập"

  return new Intl.DateTimeFormat("vi-VN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value))
}

interface UserTableProps {
  users: User[]
  pagination: PaginatedUsersResponse | null
  page: number
  pageSize: number
  loading: boolean
  currentUserId?: string
  onPageChange: (page: number) => void
  onEdit: (user: User) => void
  onDelete: (user: User) => void
}

export function UserTable({
  users,
  pagination,
  page,
  pageSize,
  loading,
  currentUserId,
  onPageChange,
  onEdit,
  onDelete,
}: UserTableProps) {
  const columns: CommonTableColumn<User>[] = useMemo(
    () => [
      {
        id: "user",
        header: "Tài khoản",
        className: "min-w-56 whitespace-nowrap",
        cell: (user) => (
          <div className="flex min-w-48 items-center gap-3">
            <UserAvatar email={user.email} />
            <div className="min-w-0">
              <p className="truncate font-medium">{user.full_name}</p>
              <p className="truncate text-xs text-muted-foreground">
                {user.email}
              </p>
            </div>
          </div>
        ),
        skeletonClassName: "h-8 w-4/5",
      },
      {
        id: "role",
        header: "Vai trò",
        className: "min-w-36 whitespace-nowrap",
        cell: (user) => (
          <Badge variant="outline">{roleLabel(user.role_code)}</Badge>
        ),
      },
      {
        id: "status",
        header: "Trạng thái",
        className: "min-w-36 whitespace-nowrap",
        cell: (user) => <UserStatusBadge status={user.status} />,
      },
      {
        id: "createdAt",
        header: "Ngày tạo",
        className: "min-w-44 whitespace-nowrap",
        cell: (user) => formatUserDate(user.created_at),
      },
      {
        id: "lastLoginAt",
        header: "Đăng nhập gần nhất",
        className: "min-w-48 whitespace-nowrap",
        cell: (user) => formatUserDate(user.last_login_at),
      },
      {
        id: "actions",
        header: <span className="sr-only">Thao tác</span>,
        className: "w-14 text-right",
        cell: (user) => {
          const isCurrentUser = user.id === currentUserId
          const isAdmin = user.role_code === "ADMIN"
          const isActionDisabled =
            isCurrentUser || isAdmin || user.status === "DISABLED"

          return (
            <div className="flex justify-end">
              <AppDropdown
                aria-label={`Thao tác với ${user.full_name}`}
                items={[
                  {
                    key: "edit",
                    label: "Chỉnh sửa",
                    icon: <EditIcon />,
                    disabled: isActionDisabled,
                    onClick: () => onEdit(user),
                  },
                  {
                    key: "delete",
                    label: "Vô hiệu hóa",
                    icon: <Trash2Icon />,
                    variant: "destructive",
                    disabled: isActionDisabled,
                    onClick: () => onDelete(user),
                  },
                ]}
              />
            </div>
          )
        },
      },
    ],
    [currentUserId, onDelete, onEdit]
  )

  return (
    <CommonTable
      data={users}
      columns={columns}
      loading={loading}
      summary={
        loading
          ? "Đang tải tài khoản..."
          : `Hiển thị ${users.length} / ${pagination?.total ?? 0} tài khoản`
      }
      getRowId={(user) => user.id}
      emptyMessage={
        <EmptyTableState
          title="Không tìm thấy tài khoản"
          description="Thử đổi từ khóa tìm kiếm hoặc tạo tài khoản mới."
        />
      }
      pagination={{
        page,
        pageSize,
        total: pagination?.total ?? 0,
        totalPages: pagination?.pages ?? 1,
        hasPrevious: page > 1,
        hasNext: page < (pagination?.pages ?? 1),
        onPageChange,
      }}
    />
  )
}
