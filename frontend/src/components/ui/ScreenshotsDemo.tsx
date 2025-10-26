import React from 'react';
import { Button } from './button';

const arr = ['Dashboard', 'Подборки', 'ИИ-помощник'];

const ScreenshotsDemo: React.FC = () => {
  return (
    <div className="w-full">
      <div className="flex justify-between items-center pb-10">
        <div>
          <h2 className="text-2xl font-bold pb-3">Скриншоты продукта</h2>
          <p>Дашборды, подборки, ИИ-чат и мониторинг - готово из коробки.</p>
        </div>
          <Button className='bg-blue-500'>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              className="size-5"
            >
              <path
                fillRule="evenodd"
                d="M4.606 12.97a.75.75 0 0 1-.134 1.051 2.494 2.494 0 0 0-.93 2.437 2.494 2.494 0 0 0 2.437-.93.75.75 0 1 1 1.186.918 3.995 3.995 0 0 1-4.482 1.332.75.75 0 0 1-.461-.461 3.994 3.994 0 0 1 1.332-4.482.75.75 0 0 1 1.052.134Z"
                clipRule="evenodd"
              />
              <path
                fillRule="evenodd"
                d="M5.752 12A13.07 13.07 0 0 0 8 14.248v4.002c0 .414.336.75.75.75a5 5 0 0 0 4.797-6.414 12.984 12.984 0 0 0 5.45-10.848.75.75 0 0 0-.735-.735 12.984 12.984 0 0 0-10.849 5.45A5 5 0 0 0 1 11.25c.001.414.337.75.751.75h4.002ZM13 9a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z"
                clipRule="evenodd"
              />
            </svg>
            Открыть демо
          </Button>
      </div>
      <div>
        <ul className="flex gap-5">
          {arr.map((item) => (
            <li className="h-100 w-100 border">{item}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ScreenshotsDemo;
