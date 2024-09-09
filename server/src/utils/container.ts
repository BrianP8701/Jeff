import { Container, ContainerModule, interfaces } from 'inversify'
import dotenv from 'dotenv'
import { PrismaClient } from '@prisma/client'
import OpenAI from 'openai'

dotenv.config();

export const container = new Container({
  autoBindInjectable: true,
  skipBaseClassChecks: true,
  defaultScope: 'Singleton',
})

export const TYPES = {
  Logger: Symbol.for('Logger'),
  LoggerFactory: Symbol.for('LoggerFactory'),
}

export const coreBindingsModule = new ContainerModule((bind: interfaces.Bind) => {

  const prismaClient = new PrismaClient({
    log: [
      { emit: 'event', level: 'info' },
      { emit: 'event', level: 'warn' },
      { emit: 'event', level: 'error' },
    ],
  })
  bind(PrismaClient).toConstantValue(prismaClient)

  bind(OpenAI).toConstantValue(new OpenAI({ apiKey: process.env.OPENAI_API_KEY }))
})

container.load(coreBindingsModule)
