import { PlusIcon, SearchIcon } from "lucide-react"

import { ConfirmDeleteDialog } from "@/components/admin/management/confirm-delete-dialog"
import { AppSelect, type SelectOption } from "@/components/common/app-select"
import { Button } from "@/components/ui/button"
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group"
import { useUserManagement } from "@/hooks/use-user-management"
import { UserFormSheet } from "@/features/user-management/user-form-sheet"
import { UserTable } from "@/features/user-management/user-table"
import { MANAGEABLE_USER_ROLES, USER_ROLE_LABELS } from "@/types/user"
import type {
  UserRoleFilter,
  UserSortOption,
  UserStatusFilter,
} from "@/types/user-management"

const ROLE_FILTER_OPTIONS: SelectOption<UserRoleFilter>[] = [
  { value: "ALL", label: "Tất cả vai trò" },
  ...MANAGEABLE_USER_ROLES.map((role) => ({
    value: role,
    label: USER_ROLE_LABELS[role],
  })),
]

const STATUS_FILTER_OPTIONS: SelectOption<UserStatusFilter>[] = [
  { value: "ALL", label: "Tất cả trạng thái" },
  { value: "ACTIVE", label: "Đang hoạt động" },
  { value: "DISABLED", label: "Đã vô hiệu hóa" },
  { value: "LOCKED", label: "Đang bị khóa" },
]

const SORT_OPTIONS: SelectOption<UserSortOption>[] = [
  { value: "created_at_desc", label: "Ngày tạo: mới → cũ" },
  { value: "created_at_asc", label: "Ngày tạo: cũ → mới" },
  { value: "full_name_asc", label: "Tên: A → Z" },
  { value: "full_name_desc", label: "Tên: Z → A" },
  { value: "last_login_at_desc", label: "Lần đăng nhập: mới → cũ" },
  { value: "last_login_at_asc", label: "Lần đăng nhập: cũ → mới" },
]

export function UserManagementPage() {
  const userManagement = useUserManagement()

  return (
    <div className="mx-auto flex w-full min-w-0 flex-col gap-4">
      <header className="px-3 pt-3">
        <h1 className="text-2xl font-semibold">Quản lý tài khoản</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Quản lý thông tin, vai trò và trạng thái truy cập của người dùng.
        </p>
      </header>
      <div className="flex min-w-0 flex-col gap-4">
        <div className="flex flex-col gap-2 px-3 xl:flex-row">
          <InputGroup className="xl:max-w-xs">
            <InputGroupAddon>
              <SearchIcon />
            </InputGroupAddon>
            <InputGroupInput
              value={userManagement.search}
              disabled={userManagement.loading}
              onChange={(event) =>
                userManagement.updateSearch(event.target.value)
              }
              placeholder="Tìm tên hoặc email..."
              aria-label="Tìm kiếm tài khoản"
            />
          </InputGroup>
          <AppSelect
            aria-label="Lọc theo vai trò"
            className="w-full xl:w-44"
            disabled={userManagement.loading}
            value={userManagement.roleFilter}
            onChange={userManagement.updateRoleFilter}
            options={ROLE_FILTER_OPTIONS}
          />
          <AppSelect
            aria-label="Lọc theo trạng thái"
            className="w-full xl:w-48"
            disabled={userManagement.loading}
            value={userManagement.statusFilter}
            onChange={userManagement.updateStatusFilter}
            options={STATUS_FILTER_OPTIONS}
          />
          <AppSelect
            aria-label="Sắp xếp tài khoản"
            className="w-full xl:w-48"
            disabled={userManagement.loading}
            value={userManagement.sort}
            onChange={userManagement.updateSort}
            options={SORT_OPTIONS}
          />
          {userManagement.hasActiveFilters ? (
            <Button
              type="button"
              variant="ghost"
              disabled={userManagement.loading}
              onClick={userManagement.resetFilters}
            >
              Xoá bộ lọc
            </Button>
          ) : null}
          <Button
            disabled={userManagement.loading}
            onClick={() => userManagement.openUserSheet()}
            className="xl:ml-auto"
          >
            <PlusIcon data-icon="inline-start" />
            Thêm tài khoản
          </Button>
        </div>

        <UserTable
          users={userManagement.users}
          pagination={userManagement.pagination}
          page={userManagement.page}
          pageSize={userManagement.pageSize}
          loading={userManagement.loading}
          currentUserId={userManagement.currentUserId}
          onPageChange={userManagement.setPage}
          onEdit={userManagement.openUserSheet}
          onDelete={userManagement.requestDelete}
        />
      </div>

      <UserFormSheet
        open={userManagement.sheetOpen}
        onOpenChange={userManagement.handleSheetOpenChange}
        user={userManagement.editingUser}
        onSave={userManagement.handleSave}
      />
      <ConfirmDeleteDialog
        target={userManagement.deleteTarget}
        isLoading={userManagement.deleteLoading}
        onOpenChange={userManagement.handleDeleteDialogOpenChange}
        onConfirm={userManagement.handleDelete}
      />
    </div>
  )
}
