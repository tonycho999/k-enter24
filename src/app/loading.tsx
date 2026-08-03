// src/app/loading.tsx
export default function Loading() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
      {/* 빙글빙글 도는 심플한 로딩 스피너 */}
      <div className="spinner"></div>
      
      {/* globals.css에 .spinner 스타일을 추가해야 작동합니다 (아래 설명 참고) */}
    </div>
  );
}
