export interface DeleteTarget {
  type: "product" | "customer" | "category" | "user"
  id: string
  name: string
}
