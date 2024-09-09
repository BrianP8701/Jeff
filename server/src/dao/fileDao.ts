import { PrismaClient, Prisma } from '@prisma/client';
import { container } from '../utils/container';

export async function createFile(data: Prisma.FileCreateInput) {
  const prisma = container.get(PrismaClient);
  return prisma.file.create({ data });
}

export async function getFile(id: string) {
  const prisma = container.get(PrismaClient);
  return prisma.file.findUnique({ where: { id } });
}

export async function updateFile(id: string, data: Prisma.FileUpdateInput) {
  const prisma = container.get(PrismaClient);
  return prisma.file.update({ where: { id }, data });
}

export async function deleteFile(id: string) {
  const prisma = container.get(PrismaClient);
  return prisma.file.delete({ where: { id } });
}
