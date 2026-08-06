import { useMemo } from "react"
import { FilterXIcon, SearchIcon } from "lucide-react"
import { debounce, defaultRateLimit, parseAsString, useQueryStates } from "nuqs"

import { ClientPageLayout } from "@/components/client-page-layout"
import { ProductCard } from "@/components/product-card"
import { Button } from "@/components/ui/button"
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty"
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group"
import { Panel, PanelContent, Separator } from "@/components/ui/panel"
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useDebounce } from "@/hooks/use-debounce"
import { normalizeProductText, products } from "@/lib/products"

const clientProductQueryParsers = {
  search: parseAsString.withDefault(""),
  category: parseAsString.withDefault("all"),
}
const clientProductQueryOptions = { urlKeys: { search: "q" } }

export const Component = () => {
  const [{ search, category }, setQuery] = useQueryStates(
    clientProductQueryParsers,
    clientProductQueryOptions
  )
  const debouncedSearch = useDebounce(search, 300)

  const categories = useMemo(
    () =>
      Array.from(new Set(products.map((product) => product.category))).sort(
        (first, second) => first.localeCompare(second, "vi")
      ),
    []
  )

  const filteredProducts = useMemo(() => {
    const query = normalizeProductText(debouncedSearch.trim())

    return products.filter((product) => {
      const matchesSearch =
        !query ||
        [product.name, product.category, product.shortDescription].some(
          (value) => normalizeProductText(value).includes(query)
        )
      const matchesCategory =
        category === "all" || product.category === category

      return matchesSearch && matchesCategory
    })
  }, [category, debouncedSearch])

  const resetFilters = () => {
    void setQuery({ search: "", category: "all" })
  }

  const updateSearch = (value: string) => {
    void setQuery(
      { search: value },
      { limitUrlUpdates: value ? debounce(300) : defaultRateLimit }
    )
  }

  return (
    <ClientPageLayout>
      <Panel className="screen-border-bottom-none screen-border-top-none">
        <PanelContent className="p-4">
          <h1 className="text-xl font-bold">Sản phẩm</h1>
          <p className="text-sm text-muted-foreground">
            Khám phá những sản phẩm được lựa chọn dành cho bạn.
          </p>
        </PanelContent>
      </Panel>

      <Panel>
        <PanelContent className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <InputGroup className="sm:flex-1">
            <InputGroupAddon>
              <SearchIcon />
            </InputGroupAddon>
            <InputGroupInput
              value={search}
              onChange={(event) => updateSearch(event.target.value)}
              placeholder="Tìm tên sản phẩm..."
              aria-label="Tìm kiếm sản phẩm"
            />
          </InputGroup>
          <Select
            value={category}
            onValueChange={(value) =>
              void setQuery({ category: value ?? "all" })
            }
          >
            <SelectTrigger className="w-full sm:w-56">
              <SelectValue>
                {category === "all" ? "Tất cả danh mục" : category}
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectItem value="all">Tất cả danh mục</SelectItem>
                {categories.map((item) => (
                  <SelectItem key={item} value={item}>
                    {item}
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>
          {(search || category !== "all") && (
            <Button type="button" variant="ghost" onClick={resetFilters}>
              <FilterXIcon data-icon="inline-start" />
              Xoá lọc
            </Button>
          )}
        </PanelContent>
      </Panel>

      <Panel>
        {filteredProducts.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {filteredProducts.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        ) : (
          <Empty className="border-0">
            <EmptyHeader>
              <EmptyMedia variant="icon">
                <SearchIcon />
              </EmptyMedia>
              <EmptyTitle>Không tìm thấy sản phẩm</EmptyTitle>
              <EmptyDescription>
                Thử đổi từ khoá hoặc chọn lại danh mục để xem thêm sản phẩm.
              </EmptyDescription>
            </EmptyHeader>
          </Empty>
        )}
      </Panel>

      <Separator />
    </ClientPageLayout>
  )
}

export default Component
