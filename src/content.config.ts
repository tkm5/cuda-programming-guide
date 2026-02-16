import { defineCollection, z } from 'astro:content'
import { glob } from 'astro/loaders'

const sections = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/data/sections' }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      description: z.string(),
      sectionNumber: z.number().int().min(1).max(12),
      sectionTitle: z.string(),
      lectureNumber: z.number().int().min(0),
      lectureTitle: z.string().optional(),
      difficulty: z
        .enum(['beginner', 'intermediate', 'advanced'])
        .default('beginner'),
      tags: z.array(z.string()).default([]),
      category: z
        .enum([
          'gpu-hardware',
          'setup',
          'cuda-basics',
          'profiling',
          'performance',
          'indexing',
          'memory-optimization',
          'debugging',
          'algorithms',
        ])
        .default('gpu-hardware'),
      thumbnail: image().optional(),
      order: z.number().int(),
    }),
})

export const collections = { sections }
