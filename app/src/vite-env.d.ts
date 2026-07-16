/// <reference types="vite/client" />

// YAML files are transformed to a parsed object at build time (see yamlPlugin in vite.config.ts).
// The shape is validated at the boundary by parseRubric() in src/lib/rubric.ts, so it enters the
// app as `unknown` rather than an unchecked `any`.
declare module "*.yaml" {
  const data: unknown;
  export default data;
}
declare module "*.yml" {
  const data: unknown;
  export default data;
}
