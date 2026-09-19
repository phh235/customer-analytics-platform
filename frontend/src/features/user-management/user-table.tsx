import { useMemo } from "react"
import { EditIcon, Trash2Icon } from "lucide-react"

import { EmptyTableState } from "@/components/admin/management/empty-table-state"
import { TableActions } from "@/components/common/table-actions"
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
import { formatDateTime } from "@/lib/date"

const roleLabel = (role: UserRole) => USER_ROLE_LABELS[role]

function UserStatusBadge({ status }: { status: UserStatus }) {
  const content = {
    ACTIVE: { label: "Đang hoạt động", variant: "success" as const },
    DISABLED: { label: "Đã vô hiệu hóa", variant: "destructive" as const },
    LOCKED: { label: "Đang bị khóa", variant: "warning" as const },
  }[status]

  return <Badge variant={content.variant}>{content.label}</Badge>
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
  const visibleUsers = useMemo(
    () => users.filter((user) => user.role_code !== "ADMIN"),
    [users]
  )
  const hiddenAdminCount = users.length - visibleUsers.length
  const visibleTotal = Math.max(
    0,
    (pagination?.total ?? visibleUsers.length) - hiddenAdminCount
  )
  const visiblePages = Math.max(1, Math.ceil(visibleTotal / pageSize))
  const columns: CommonTableColumn<User>[] = useMemo(
    () => [
      {
        id: "user",
        header: "Tài khoản",
        className: "min-w-56 whitespace-nowrap",
        cell: (user) => (
          <div className="flex min-w-48 items-center gap-3">
            <UserAvatar email={user.email} name={user.full_name} />
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
          <Badge variant="secondary">{roleLabel(user.role_code)}</Badge>
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
        cell: (user) => formatDateTime(user.created_at),
      },
      {
        id: "lastLoginAt",
        header: "Đăng nhập gần nhất",
        className: "min-w-48 whitespace-nowrap",
        cell: (user) => formatDateTime(user.last_login_at, "Chưa đăng nhập"),
      },
      {
        id: "actions",
        header: "Thao tác",
        className: "w-24 text-right",
        cell: (user) => {
          const isCurrentUser = user.id === currentUserId
          const isActionDisabled = isCurrentUser || user.status === "DISABLED"

          return (
            <TableActions
              actions={[
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
          )
        },
      },
    ],
    [currentUserId, onDelete, onEdit]
  )

  return (
    <CommonTable
      data={visibleUsers}
      columns={columns}
      loading={loading}
      itemLabel="tài khoản"
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
        total: visibleTotal,
        totalPages: visiblePages,
        hasPrevious: page > 1,
        hasNext: page < visiblePages,
        onPageChange,
      }}
    />
  )
}
