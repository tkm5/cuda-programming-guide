import { getCollection } from 'astro:content'
import type { CollectionEntry } from 'astro:content'

export type SectionEntry = CollectionEntry<'sections'>

export interface SectionGroup {
  sectionNumber: number
  sectionTitle: string
  lectures: SectionEntry[]
  overview?: SectionEntry
}

/** ベースパスを取得する（末尾スラッシュなし） */
const BASE = import.meta.env.BASE_URL.replace(/\/$/, '')

/**
 * パスにベースパスを付与する
 */
export function withBase(path: string): string {
  return `${BASE}${path}`
}

/**
 * セクション番号を2桁のゼロパディング文字列に変換する
 */
export function padSection(num: number): string {
  return String(num).padStart(2, '0')
}

/**
 * レクチャー番号を2桁のゼロパディング文字列に変換する
 */
export function padLecture(num: number): string {
  return String(num).padStart(2, '0')
}

/**
 * 全セクションのデータをグループ化して取得する
 */
export async function getSectionGroups(): Promise<SectionGroup[]> {
  const allEntries = await getCollection('sections')

  const groupMap = new Map<number, SectionGroup>()

  for (const entry of allEntries) {
    const { sectionNumber, sectionTitle, lectureNumber } = entry.data

    if (!groupMap.has(sectionNumber)) {
      groupMap.set(sectionNumber, {
        sectionNumber,
        sectionTitle,
        lectures: [],
      })
    }

    const group = groupMap.get(sectionNumber)!

    if (lectureNumber === 0) {
      group.overview = entry
    } else {
      group.lectures.push(entry)
    }
  }

  // レクチャー番号順でソート
  for (const group of groupMap.values()) {
    group.lectures.sort((a, b) => a.data.lectureNumber - b.data.lectureNumber)
  }

  return Array.from(groupMap.values()).sort(
    (a, b) => a.sectionNumber - b.sectionNumber
  )
}

/**
 * 特定セクションのエントリを取得する
 */
export async function getSectionEntries(
  sectionNumber: number
): Promise<SectionEntry[]> {
  const allEntries = await getCollection('sections')
  return allEntries
    .filter((e) => e.data.sectionNumber === sectionNumber)
    .sort((a, b) => a.data.lectureNumber - b.data.lectureNumber)
}

/**
 * セクションのURLパスを生成する
 */
export function getSectionPath(sectionNumber: number): string {
  return withBase(`/sections/${padSection(sectionNumber)}`)
}

/**
 * レクチャーのURLパスを生成する
 */
export function getLecturePath(
  sectionNumber: number,
  lectureNumber: number
): string {
  return withBase(`/sections/${padSection(sectionNumber)}/lecture-${padLecture(lectureNumber)}`)
}
