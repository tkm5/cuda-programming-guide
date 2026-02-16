import { getCollection } from 'astro:content'
import type { SectionEntry } from './sections'
import { getSectionPath, getLecturePath } from './sections'

export interface NavItem {
  title: string
  path: string
  sectionNumber: number
  lectureNumber: number
}

export interface SectionTree {
  sectionNumber: number
  sectionTitle: string
  path: string
  lectures: NavItem[]
}

/**
 * サイドバー用のセクションツリーを構築する
 */
export async function buildSectionTree(): Promise<SectionTree[]> {
  const allEntries = await getCollection('sections')

  const treeMap = new Map<number, SectionTree>()

  for (const entry of allEntries) {
    const { sectionNumber, sectionTitle, lectureNumber, title } = entry.data

    if (!treeMap.has(sectionNumber)) {
      treeMap.set(sectionNumber, {
        sectionNumber,
        sectionTitle,
        path: getSectionPath(sectionNumber),
        lectures: [],
      })
    }

    if (lectureNumber > 0) {
      treeMap.get(sectionNumber)!.lectures.push({
        title,
        path: getLecturePath(sectionNumber, lectureNumber),
        sectionNumber,
        lectureNumber,
      })
    }
  }

  // ソート
  for (const tree of treeMap.values()) {
    tree.lectures.sort((a, b) => a.lectureNumber - b.lectureNumber)
  }

  return Array.from(treeMap.values()).sort(
    (a, b) => a.sectionNumber - b.sectionNumber
  )
}

/**
 * 前後のレクチャーを取得する
 */
export async function getAdjacentLectures(
  currentSection: number,
  currentLecture: number
): Promise<{ prev: NavItem | null; next: NavItem | null }> {
  const allEntries = await getCollection('sections')

  // lectureNumber > 0 のエントリのみ対象
  const lectures = allEntries
    .filter((e) => e.data.lectureNumber > 0)
    .sort((a, b) => a.data.order - b.data.order)

  const currentOrder = currentSection * 100 + currentLecture
  const currentIndex = lectures.findIndex((e) => e.data.order === currentOrder)

  if (currentIndex === -1) {
    return { prev: null, next: null }
  }

  const toNavItem = (entry: SectionEntry): NavItem => ({
    title: entry.data.title,
    path: getLecturePath(entry.data.sectionNumber, entry.data.lectureNumber),
    sectionNumber: entry.data.sectionNumber,
    lectureNumber: entry.data.lectureNumber,
  })

  const prev = currentIndex > 0 ? toNavItem(lectures[currentIndex - 1]) : null
  const next =
    currentIndex < lectures.length - 1
      ? toNavItem(lectures[currentIndex + 1])
      : null

  return { prev, next }
}
