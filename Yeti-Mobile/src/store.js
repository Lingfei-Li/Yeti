
// This connects the reducer to the store
export default function configureStore() {
  let store = createStore(reducer);

  return store
}