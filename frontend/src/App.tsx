import { RouterProvider } from 'react-router-dom';
import { router } from './router';
import { FiltrosProvider } from './store/FiltrosContext';
import './App.css';

function App() {
  return (
    <FiltrosProvider>
      <RouterProvider router={router} />
    </FiltrosProvider>
  );
}

export default App;
