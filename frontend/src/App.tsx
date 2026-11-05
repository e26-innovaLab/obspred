import { RouterProvider } from 'react-router-dom';
import { router } from './router';
import { FiltrosProvider } from './store/FiltrosContext';
import { InformeProvider } from './store/InformeContext';
import './App.css';

function App() {
  return (
    <InformeProvider>
      <FiltrosProvider>
        <RouterProvider router={router} />
      </FiltrosProvider>
    </InformeProvider>
  );
}

export default App;
