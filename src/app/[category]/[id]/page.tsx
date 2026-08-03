export default function PostDetail({ params }: { params: { category: string, id: string } }) {
  // 실제 환경에서는 params.id로 DB에서 글을 조회합니다.
  
  return (
    <article className="max-w-3xl mx-auto bg-white p-8 rounded-2xl shadow-sm">
      <header className="mb-8">
        <span className="text-sm font-bold text-pink-500 uppercase tracking-wider">
          {params.category.replace('-', ' ')}
        </span>
        <h1 className="text-4xl font-extrabold mt-3 mb-4 leading-tight">
          BTS Jin Returns: What to Expect in 2026
        </h1>
        <div className="text-slate-500 flex items-center gap-4 text-sm">
          <span>By K-ENTER24 Editor</span>
          <span>•</span>
          <span>Aug 3, 2026</span>
        </div>
      </header>

      <div className="prose prose-lg max-w-none text-slate-700">
        {/* 첫 번째 메인 이미지 */}
        <div className="w-full h-80 bg-slate-200 rounded-xl mb-8 flex items-center justify-center text-slate-400">
          Main Image (1200x630)
        </div>
        
        <p>Jin has officially returned... (Translated content paragraph 1)</p>
        <p>Fans around the world are celebrating... (Translated content paragraph 2)</p>

        {/* 두 번째 본문 이미지 */}
        <div className="w-full h-80 bg-slate-200 rounded-xl my-8 flex items-center justify-center text-slate-400">
          Sub Image 1
        </div>
        
        <p>According to real-time reports from Korea... (Translated content paragraph 3)</p>
        
        {/* 세 번째 본문 이미지 */}
        <div className="w-full h-80 bg-slate-200 rounded-xl my-8 flex items-center justify-center text-slate-400">
          Sub Image 2
        </div>
        
        <p>This marks a new era for the group... (Translated content paragraph 4)</p>
      </div>
    </article>
  );
}
