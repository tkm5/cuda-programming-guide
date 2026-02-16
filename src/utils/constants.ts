export const SITE_TITLE = 'CUDA プログラミング完全ガイド'
export const SITE_DESCRIPTION =
  'Udemyコース「Mastering GPU Parallel Programming with CUDA」の日本語解説サイト．全12セクション，60レクチャーを網羅的に解説します．'
export const COURSE_ID = 4267614
export const TOTAL_SECTIONS = 12
export const TOTAL_LECTURES = 60
export const TOTAL_QUIZZES = 2

export const SECTION_TITLES: Record<number, string> = {
  1: 'Introduction to the Nvidia GPUs hardware',
  2: 'Installing CUDA and other programs',
  3: 'Introduction to CUDA programming',
  4: 'Profiling',
  5: 'Performance analysis for the previous applications',
  6: '2D Indexing',
  7: 'Shared Memory + Warp Divergence',
  8: 'Debugging tools',
  9: 'Vector Reduction',
  10: 'Roofline model',
  11: 'Matrix Multiplication (Bonus)',
  12: 'Profiling - nsight systems',
}

export const SECTION_CATEGORIES: Record<number, string> = {
  1: 'gpu-hardware',
  2: 'setup',
  3: 'cuda-basics',
  4: 'profiling',
  5: 'performance',
  6: 'indexing',
  7: 'memory-optimization',
  8: 'debugging',
  9: 'algorithms',
  10: 'performance',
  11: 'algorithms',
  12: 'profiling',
}
