import create from 'zustand'
import { produce } from 'immer'

// https://github.com/react-spring/zustand#middleware
// Log every time state is changed
// const log = (config: any) => (set: any, get: any, api: any) =>
//   config(
//     (args: any) => {
//       set(args);
//       console.info('%cNew State:', 'font-weight: bold; color: #bada55;');
//       console.info(get());
//     },
//     get,
//     api
//   );

const immer = (config: any) => (set: any, get: any, api: any) =>
  config(
    (fn: any) => {
      // console.info('%cApplying:', 'font-weight: bold; color: cornflowerblue;');
      // console.info(fn);
      set(produce(fn))
    },
    get,
    api
  )

export function createStore(store: unknown) {
  // if (process.env.NODE_ENV === 'development') {
  //   // prettier-ignore
  //   return create(
  //     log(
  //       immer(
  //         store
  //       )
  //     )
  //   );
  // } else {
  return create(immer(store))
  // }
}
