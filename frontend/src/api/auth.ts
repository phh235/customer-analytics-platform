import apiClient from "./client"

export async function loginDemo() {
  const { data } = await apiClient.post<{ token: string }>("/auth/login")
  return data
}
