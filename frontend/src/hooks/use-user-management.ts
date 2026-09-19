import { useCallback, useEffect, useState } from "react"
import {
  queryOptions,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query"
import {
  parseAsInteger,
  parseAsString,
  parseAsStringLiteral,
  useQueryStates,
} from "nuqs"

import { getApiErrorMessage } from "@/api/errors"
import { createUser, deleteUser, listUsers, updateUser } from "@/api/users"
import type { DeleteTarget } from "@/components/admin/management/types"
import { useDebounce } from "@/hooks/use-debounce"
import { useAuthStore } from "@/stores/use-auth-store"
import { useLoadingStore } from "@/stores/use-loading-store"
import type { User } from "@/types/user"
import type {
  ListUsersParams,
  SortOrder,
  UserFormData,
  UserRoleFilter,
  UserSortField,
  UserSortOption,
  UserStatusFilter,
} from "@/types/user-management"
import { toastError, toastSuccess } from "@/utils/toast"

const EMPTY_USERS: User[] = []
const USER_PAGE_SIZE = 10
const DEFAULT_SORT: UserSortOption = "created_at_desc"
const MANAGEABLE_ROLE_FILTERS = [
  "ALL",
  "MANAGER",
  "ANALYST",
  "SALES",
  "CSKH",
  "USER",
] as const

const USER_SORT_PARAMS: Record<
  UserSortOption,
  { sortBy: UserSortField; sortOrder: SortOrder }
> = {
  created_at_desc: { sortBy: "created_at", sortOrder: "desc" },
  created_at_asc: { sortBy: "created_at", sortOrder: "asc" },
  full_name_asc: { sortBy: "full_name", sortOrder: "asc" },
  full_name_desc: { sortBy: "full_name", sortOrder: "desc" },
  last_login_at_desc: { sortBy: "last_login_at", sortOrder: "desc" },
  last_login_at_asc: { sortBy: "last_login_at", sortOrder: "asc" },
}

const normalizeUserListParams = (params: ListUsersParams) => ({
  page: params.page ?? 1,
  size: params.size ?? USER_PAGE_SIZE,
  search: params.search?.trim() ?? "",
  role_code: params.role_code,
  status: params.status,
  sort_by: params.sort_by ?? "created_at",
  sort_order: params.sort_order ?? "desc",
})

const userQueryKeys = {
  all: ["users"] as const,
  list: (params: ListUsersParams) =>
    ["users", "list", normalizeUserListParams(params)] as const,
}

function usersQueryOptions(params: ListUsersParams) {
  const normalizedParams = normalizeUserListParams(params)

  return queryOptions({
    queryKey: userQueryKeys.list(normalizedParams),
    queryFn: () => listUsers(normalizedParams),
    refetchOnMount: "always",
  })
}

export function useUserManagement() {
  const currentUserId = useAuthStore((state) => state.user?.id)
  const startGlobalLoading = useLoadingStore((state) => state.startLoading)
  const stopGlobalLoading = useLoadingStore((state) => state.stopLoading)
  const queryClient = useQueryClient()
  const [{ search, roleFilter, statusFilter, sort, page }, setQuery] =
    useQueryStates(
      {
        search: parseAsString.withDefault(""),
        roleFilter: parseAsStringLiteral(MANAGEABLE_ROLE_FILTERS).withDefault(
          "ALL"
        ),
        statusFilter: parseAsStringLiteral([
          "ALL",
          "ACTIVE",
          "DISABLED",
          "LOCKED",
        ] as const).withDefault("ALL"),
        sort: parseAsStringLiteral([
          "created_at_desc",
          "created_at_asc",
          "full_name_asc",
          "full_name_desc",
          "last_login_at_desc",
          "last_login_at_asc",
        ] as const).withDefault(DEFAULT_SORT),
        page: parseAsInteger.withDefault(1),
      },
      {
        urlKeys: {
          search: "q",
          roleFilter: "role",
          statusFilter: "status",
        },
      }
    )
  const debouncedSearch = useDebounce(search, 300)
  const [sheetOpen, setSheetOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<DeleteTarget | null>(null)
  const sortParams = USER_SORT_PARAMS[sort]

  const usersQuery = useQuery(
    usersQueryOptions({
      page,
      size: USER_PAGE_SIZE,
      search: debouncedSearch,
      role_code: roleFilter === "ALL" ? undefined : roleFilter,
      status: statusFilter === "ALL" ? undefined : statusFilter,
      sort_by: sortParams.sortBy,
      sort_order: sortParams.sortOrder,
    })
  )
  const users = usersQuery.data?.records ?? EMPTY_USERS
  const loading = usersQuery.isPending || usersQuery.isFetching

  useEffect(() => {
    if (!usersQuery.isFetching) return

    startGlobalLoading()
    return () => stopGlobalLoading()
  }, [startGlobalLoading, stopGlobalLoading, usersQuery.isFetching])

  useEffect(() => {
    if (!usersQuery.error) return

    toastError(
      getApiErrorMessage(usersQuery.error, "Không thể tải danh sách tài khoản.")
    )
  }, [usersQuery.error])

  const saveUserMutation = useMutation({
    mutationFn: async ({
      user,
      data,
    }: {
      user: User | null
      data: UserFormData
    }) => {
      if (user) {
        return updateUser(user.id, {
          full_name: data.full_name,
          role_code: data.role_code,
          status: data.status,
        })
      }

      return createUser({
        email: data.email,
        password: data.password ?? "",
        full_name: data.full_name,
        role_code: data.role_code,
      })
    },
    onMutate: () => startGlobalLoading(),
    onSuccess: async (_, variables) => {
      toastSuccess(
        variables.user ? "Đã cập nhật tài khoản" : "Đã tạo tài khoản mới"
      )
      setSheetOpen(false)
      setEditingUser(null)

      if (!variables.user && page !== 1) void setQuery({ page: 1 })
      await queryClient.invalidateQueries({ queryKey: userQueryKeys.all })
    },
    onError: (error) => {
      toastError(getApiErrorMessage(error, "Không thể lưu tài khoản."))
    },
    onSettled: () => stopGlobalLoading(),
  })

  const deleteUserMutation = useMutation({
    mutationFn: (userId: string) => deleteUser(userId),
    onMutate: () => startGlobalLoading(),
    onSuccess: async () => {
      toastSuccess("Đã vô hiệu hóa tài khoản")
      setDeleteTarget(null)
      if (users.length === 1 && page > 1) {
        void setQuery({ page: page - 1 })
      }
      await queryClient.invalidateQueries({ queryKey: userQueryKeys.all })
    },
    onError: (error) => {
      toastError(getApiErrorMessage(error, "Không thể vô hiệu hóa tài khoản."))
    },
    onSettled: () => stopGlobalLoading(),
  })

  const updateSearch = useCallback(
    (value: string) => void setQuery({ search: value, page: 1 }),
    [setQuery]
  )

  const updateRoleFilter = useCallback(
    (value: UserRoleFilter) =>
      void setQuery({
        roleFilter: value as (typeof MANAGEABLE_ROLE_FILTERS)[number],
        page: 1,
      }),
    [setQuery]
  )

  const updateStatusFilter = useCallback(
    (value: UserStatusFilter) =>
      void setQuery({ statusFilter: value, page: 1 }),
    [setQuery]
  )

  const updateSort = useCallback(
    (value: UserSortOption) => void setQuery({ sort: value, page: 1 }),
    [setQuery]
  )

  const resetFilters = useCallback(() => void setQuery(null), [setQuery])

  const openUserSheet = useCallback((user: User | null = null) => {
    setEditingUser(user)
    setSheetOpen(true)
  }, [])

  const handleSheetOpenChange = useCallback((open: boolean) => {
    setSheetOpen(open)
    if (!open) setEditingUser(null)
  }, [])

  const requestDelete = useCallback((user: User) => {
    setDeleteTarget({
      type: "user",
      id: user.id,
      name: user.full_name,
    })
  }, [])

  const handleDeleteDialogOpenChange = useCallback(
    (open: boolean) => {
      if (!open && !deleteUserMutation.isPending) setDeleteTarget(null)
    },
    [deleteUserMutation.isPending]
  )

  const handleSave = async (data: UserFormData) => {
    try {
      await saveUserMutation.mutateAsync({ user: editingUser, data })
    } catch {
      // The mutation already displays the mapped API error.
    }
  }

  const handleDelete = async () => {
    if (!deleteTarget || deleteUserMutation.isPending) return

    try {
      await deleteUserMutation.mutateAsync(deleteTarget.id)
    } catch {
      // The mutation already displays the mapped API error.
    }
  }

  return {
    currentUserId,
    users,
    pagination: usersQuery.data ?? null,
    pageSize: USER_PAGE_SIZE,
    loading,
    search,
    roleFilter,
    statusFilter,
    sort,
    hasActiveFilters:
      search.length > 0 ||
      roleFilter !== "ALL" ||
      statusFilter !== "ALL" ||
      sort !== DEFAULT_SORT,
    page,
    setPage: (nextPage: number) => void setQuery({ page: nextPage }),
    updateSearch,
    updateRoleFilter,
    updateStatusFilter,
    updateSort,
    resetFilters,
    sheetOpen,
    editingUser,
    openUserSheet,
    handleSheetOpenChange,
    handleSave,
    deleteTarget,
    deleteLoading: deleteUserMutation.isPending,
    requestDelete,
    handleDeleteDialogOpenChange,
    handleDelete,
  }
}
