import { PrismaClient, Prisma } from '@prisma/client';
import { container } from '../utils/container';

export async function createEmail(data: Prisma.EmailCreateInput) {
  const prisma = container.get(PrismaClient);
  return prisma.email.create({ data });
}

export async function getEmail(id: string) {
  const prisma = container.get(PrismaClient);
  return prisma.email.findUnique({ where: { id } });
}

export async function updateEmail(id: string, data: Prisma.EmailUpdateInput) {
  const prisma = container.get(PrismaClient);
  return prisma.email.update({ where: { id }, data });
}

export async function deleteEmail(id: string) {
  const prisma = container.get(PrismaClient);
  return prisma.email.delete({ where: { id } });
}
