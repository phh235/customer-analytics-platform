import { LineShadowText } from "@/components/line-shadow-text"
import { Button } from "@/components/ui/button"
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyTitle,
} from "@/components/ui/empty"
import { FullWidthDivider } from "@/components/ui/full-width-divider"
import { ArrowLeft } from "lucide-react"
import { Link } from "react-router"

export const Component = () => {
  return (
    <div className="flex w-full items-center justify-center overflow-hidden">
      <div className="flex h-screen items-center border-x">
        <div className="relative">
          <FullWidthDivider position="top" />
          <Empty>
            <EmptyHeader>
              <EmptyTitle className="font-mono text-8xl font-black italic">
                <LineShadowText shadowColor="var(--color-foreground)">
                  404
                </LineShadowText>
              </EmptyTitle>
              <EmptyDescription className="text-nowrap">
                Rất tiếc, trang bạn đang tìm kiếm không tồn tại
              </EmptyDescription>
            </EmptyHeader>
            <EmptyContent>
              <Button render={<Link to="/dashboard" />}>
                <ArrowLeft />
                Quay lại
              </Button>
            </EmptyContent>
          </Empty>
          <FullWidthDivider position="bottom" />
        </div>
      </div>
    </div>
  )
}
