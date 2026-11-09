import { RouterProvider } from 'react-router-dom';
import { router } from './router';
import { FiltrosProvider } from './store/FiltrosContext';
import { InformeProvider } from './store/InformeContext';
import './App.css';

function App() {
  return (
    <FiltrosProvider>
      <InformeProvider>
        <RouterProvider router={router} />
      </InformeProvider>
    </FiltrosProvider>
  );
}

export default App;
