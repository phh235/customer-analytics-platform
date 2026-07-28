import apiClient from "./client"

export async function getHello() {
  const { data } = await apiClient.get<{ message: string }>("/hello")
  return data
}
