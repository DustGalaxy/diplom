/* eslint-disable */

// @ts-nocheck

// noinspection JSUnusedGlobalSymbols

// This file was automatically generated by TanStack Router.
// You should NOT make any changes in this file as it will be overwritten.
// Additionally, you should also exclude this file from your linter and/or formatter to prevent it from being checked or modified.

// Import Routes

import { Route as rootRoute } from './routes/__root'
import { Route as RegestrationImport } from './routes/regestration'
import { Route as PlaypageImport } from './routes/playpage'
import { Route as LogoutImport } from './routes/logout'
import { Route as LoginImport } from './routes/login'
import { Route as HomeImport } from './routes/home'
import { Route as AccountImport } from './routes/account'
import { Route as AboutImport } from './routes/about'
import { Route as IndexImport } from './routes/index'
import { Route as DemoStoreImport } from './routes/demo.store'

// Create/Update Routes

const RegestrationRoute = RegestrationImport.update({
  id: '/regestration',
  path: '/regestration',
  getParentRoute: () => rootRoute,
} as any)

const PlaypageRoute = PlaypageImport.update({
  id: '/playpage',
  path: '/playpage',
  getParentRoute: () => rootRoute,
} as any)

const LogoutRoute = LogoutImport.update({
  id: '/logout',
  path: '/logout',
  getParentRoute: () => rootRoute,
} as any)

const LoginRoute = LoginImport.update({
  id: '/login',
  path: '/login',
  getParentRoute: () => rootRoute,
} as any)

const HomeRoute = HomeImport.update({
  id: '/home',
  path: '/home',
  getParentRoute: () => rootRoute,
} as any)

const AccountRoute = AccountImport.update({
  id: '/account',
  path: '/account',
  getParentRoute: () => rootRoute,
} as any)

const AboutRoute = AboutImport.update({
  id: '/about',
  path: '/about',
  getParentRoute: () => rootRoute,
} as any)

const IndexRoute = IndexImport.update({
  id: '/',
  path: '/',
  getParentRoute: () => rootRoute,
} as any)

const DemoStoreRoute = DemoStoreImport.update({
  id: '/demo/store',
  path: '/demo/store',
  getParentRoute: () => rootRoute,
} as any)

// Populate the FileRoutesByPath interface

declare module '@tanstack/react-router' {
  interface FileRoutesByPath {
    '/': {
      id: '/'
      path: '/'
      fullPath: '/'
      preLoaderRoute: typeof IndexImport
      parentRoute: typeof rootRoute
    }
    '/about': {
      id: '/about'
      path: '/about'
      fullPath: '/about'
      preLoaderRoute: typeof AboutImport
      parentRoute: typeof rootRoute
    }
    '/account': {
      id: '/account'
      path: '/account'
      fullPath: '/account'
      preLoaderRoute: typeof AccountImport
      parentRoute: typeof rootRoute
    }
    '/home': {
      id: '/home'
      path: '/home'
      fullPath: '/home'
      preLoaderRoute: typeof HomeImport
      parentRoute: typeof rootRoute
    }
    '/login': {
      id: '/login'
      path: '/login'
      fullPath: '/login'
      preLoaderRoute: typeof LoginImport
      parentRoute: typeof rootRoute
    }
    '/logout': {
      id: '/logout'
      path: '/logout'
      fullPath: '/logout'
      preLoaderRoute: typeof LogoutImport
      parentRoute: typeof rootRoute
    }
    '/playpage': {
      id: '/playpage'
      path: '/playpage'
      fullPath: '/playpage'
      preLoaderRoute: typeof PlaypageImport
      parentRoute: typeof rootRoute
    }
    '/regestration': {
      id: '/regestration'
      path: '/regestration'
      fullPath: '/regestration'
      preLoaderRoute: typeof RegestrationImport
      parentRoute: typeof rootRoute
    }
    '/demo/store': {
      id: '/demo/store'
      path: '/demo/store'
      fullPath: '/demo/store'
      preLoaderRoute: typeof DemoStoreImport
      parentRoute: typeof rootRoute
    }
  }
}

// Create and export the route tree

export interface FileRoutesByFullPath {
  '/': typeof IndexRoute
  '/about': typeof AboutRoute
  '/account': typeof AccountRoute
  '/home': typeof HomeRoute
  '/login': typeof LoginRoute
  '/logout': typeof LogoutRoute
  '/playpage': typeof PlaypageRoute
  '/regestration': typeof RegestrationRoute
  '/demo/store': typeof DemoStoreRoute
}

export interface FileRoutesByTo {
  '/': typeof IndexRoute
  '/about': typeof AboutRoute
  '/account': typeof AccountRoute
  '/home': typeof HomeRoute
  '/login': typeof LoginRoute
  '/logout': typeof LogoutRoute
  '/playpage': typeof PlaypageRoute
  '/regestration': typeof RegestrationRoute
  '/demo/store': typeof DemoStoreRoute
}

export interface FileRoutesById {
  __root__: typeof rootRoute
  '/': typeof IndexRoute
  '/about': typeof AboutRoute
  '/account': typeof AccountRoute
  '/home': typeof HomeRoute
  '/login': typeof LoginRoute
  '/logout': typeof LogoutRoute
  '/playpage': typeof PlaypageRoute
  '/regestration': typeof RegestrationRoute
  '/demo/store': typeof DemoStoreRoute
}

export interface FileRouteTypes {
  fileRoutesByFullPath: FileRoutesByFullPath
  fullPaths:
    | '/'
    | '/about'
    | '/account'
    | '/home'
    | '/login'
    | '/logout'
    | '/playpage'
    | '/regestration'
    | '/demo/store'
  fileRoutesByTo: FileRoutesByTo
  to:
    | '/'
    | '/about'
    | '/account'
    | '/home'
    | '/login'
    | '/logout'
    | '/playpage'
    | '/regestration'
    | '/demo/store'
  id:
    | '__root__'
    | '/'
    | '/about'
    | '/account'
    | '/home'
    | '/login'
    | '/logout'
    | '/playpage'
    | '/regestration'
    | '/demo/store'
  fileRoutesById: FileRoutesById
}

export interface RootRouteChildren {
  IndexRoute: typeof IndexRoute
  AboutRoute: typeof AboutRoute
  AccountRoute: typeof AccountRoute
  HomeRoute: typeof HomeRoute
  LoginRoute: typeof LoginRoute
  LogoutRoute: typeof LogoutRoute
  PlaypageRoute: typeof PlaypageRoute
  RegestrationRoute: typeof RegestrationRoute
  DemoStoreRoute: typeof DemoStoreRoute
}

const rootRouteChildren: RootRouteChildren = {
  IndexRoute: IndexRoute,
  AboutRoute: AboutRoute,
  AccountRoute: AccountRoute,
  HomeRoute: HomeRoute,
  LoginRoute: LoginRoute,
  LogoutRoute: LogoutRoute,
  PlaypageRoute: PlaypageRoute,
  RegestrationRoute: RegestrationRoute,
  DemoStoreRoute: DemoStoreRoute,
}

export const routeTree = rootRoute
  ._addFileChildren(rootRouteChildren)
  ._addFileTypes<FileRouteTypes>()

/* ROUTE_MANIFEST_START
{
  "routes": {
    "__root__": {
      "filePath": "__root.tsx",
      "children": [
        "/",
        "/about",
        "/account",
        "/home",
        "/login",
        "/logout",
        "/playpage",
        "/regestration",
        "/demo/store"
      ]
    },
    "/": {
      "filePath": "index.tsx"
    },
    "/about": {
      "filePath": "about.tsx"
    },
    "/account": {
      "filePath": "account.tsx"
    },
    "/home": {
      "filePath": "home.tsx"
    },
    "/login": {
      "filePath": "login.tsx"
    },
    "/logout": {
      "filePath": "logout.tsx"
    },
    "/playpage": {
      "filePath": "playpage.tsx"
    },
    "/regestration": {
      "filePath": "regestration.tsx"
    },
    "/demo/store": {
      "filePath": "demo.store.tsx"
    }
  }
}
ROUTE_MANIFEST_END */
