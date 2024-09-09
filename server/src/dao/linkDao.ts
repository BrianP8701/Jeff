import { PrismaClient, Prisma } from '@prisma/client';
import { container } from '../utils/container';

export async function createLink(data: Prisma.LinkCreateInput) {
  const prisma = container.get(PrismaClient);
  return prisma.link.create({ data });
}

export async function getLink(id: string) {
  const prisma = container.get(PrismaClient);
  return prisma.link.findUnique({ where: { id } });
}

export async function updateLink(id: string, data: Prisma.LinkUpdateInput) {
  const prisma = container.get(PrismaClient);
  return prisma.link.update({ where: { id }, data });
}

export async function deleteLink(id: string) {
  const prisma = container.get(PrismaClient);
  return prisma.link.delete({ where: { id } });
}
