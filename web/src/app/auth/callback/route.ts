import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  // 로그인 후 돌아갈 주소 (기본값은 메인 페이지)
  const next = searchParams.get('next') ?? '/'

  if (code) {
    // [수정 핵심] Next.js 15+ 버전에서는 cookies() 호출 시 await가 필수입니다.
    const cookieStore = await cookies()
    
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          get(name: string) { 
            return cookieStore.get(name)?.value 
          },
          set(name: string, value: string, options: CookieOptions) {
            // 서버 측에서 쿠키를 안전하게 설정합니다.
            cookieStore.set({ name, value, ...options })
          },
          remove(name: string, options: CookieOptions) {
            // 쿠키를 삭제할 때도 set을 사용하여 만료 처리합니다.
            cookieStore.set({ name, value: '', ...options })
          },
        },
      }
    )
    
    // 구글에서 전달받은 일회용 코드를 실제 유저 세션(JWT)으로 교환합니다.
    const { error } = await supabase.auth.exchangeCodeForSession(code)
    
    if (!error) {
      return NextResponse.redirect(`${origin}${next}`)
    }
  }

  // 인증 실패 시 에러 페이지로 리다이렉트합니다.
  return NextResponse.redirect(`${origin}/auth/auth-code-error`)
}
