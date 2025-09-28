import React, { useEffect, useState } from "react";
import { useForm, usePage } from "@inertiajs/react";

interface User {
  first_name: string;
  email: string;
  company: string;
}

type UserProfileErrors = Record<string, { message: string; code: string }[]>;

interface UserProfileProps {
  user: User;
  errors?: UserProfileErrors;
  [key: string]: unknown;
}

const UserProfile: React.FC = () => {
  const { user, errors: serverErrors = {} } = usePage<UserProfileProps>().props;

  const [errors, setErrors] = useState<Record<string, string>>({});

  const { data, setData, post, processing } = useForm<User>({
    first_name: user.first_name || '',
    email: user.email || '',
    company: user.company || '',
  });

  useEffect(() => {
    const flatErrors: Record<string, string> = {};
    Object.entries(serverErrors).forEach(([key, value]) => {
      flatErrors[key] = Array.isArray(value) ? value[0].message : String(value);
    });
    setErrors(flatErrors);
  }, [serverErrors]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!data.first_name.trim()) newErrors.first_name = 'Имя обязательно';
    if (!data.email.trim()) newErrors.email = 'Email обязателен';

    setErrors(prev => ({ ...prev, ...newErrors }));
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!validate()) return;

    post('/auth/profile', {
      onSuccess: () => console.log('Profile updated successfully'),
      onError: (serverErrors) => {
        console.log('Error updating the profile', serverErrors);
      },
    });
  };

  return (
    <div className="max-w-3xl mx-auto p-6">
      {/* Заголовки */}
      <h1 className="text-3xl font-bold mb-1">Личный кабинет</h1>
      <h2 className="text-lg text-gray-600 mb-6">Управление аккаунтом и подпиской</h2>

      {/* Форма */}
      <form 
        onSubmit={handleSubmit} 
        className="bg-white border border-gray-300 shadow-sm rounded p-6 space-y-4"
      >
        {/* Название формы */}
        <h3 className="text-2xl font-semibold text-gray-800 mb-4">Информация о профиле</h3>

        {/* Имя и Email */}
        <div className="flex gap-x-4">
          <div className="flex-1">
            <label className="block text-gray-700 font-medium mb-1">Имя</label>
            <input
              type="text"
              value={data.first_name}
              onChange={(e) => {
                setData('first_name', e.target.value);
                setErrors(prev => ({ ...prev, first_name: '' }));
              }}
              className="border border-gray-300 rounded p-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.first_name && <p className="text-red-500 text-sm mt-1">{errors.first_name}</p>}
          </div>

          <div className="flex-1">
            <label className="block text-gray-700 font-medium mb-1">Email</label>
            <input
              type="email"
              value={data.email}
              onChange={(e) => {
                setData('email', e.target.value);
                setErrors(prev => ({ ...prev, email: '' }));
              }}
              className="border border-gray-300 rounded p-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
          </div>
        </div>

        {/* Компания */}
        <div>
          <label className="block text-gray-700 font-medium mb-1">Компания</label>
          <input
            type="text"
            value={data.company}
            onChange={(e) => {
              setData('company', e.target.value);
              setErrors(prev => ({ ...prev, company: '' }));
            }}
            className="border border-gray-300 rounded p-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.company && <p className="text-red-500 text-sm mt-1">{errors.company}</p>}
        </div>

        {/* Кнопка */}
        <button
          type="submit"
          disabled={processing}
          className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold rounded-lg px-6 py-2 shadow-md disabled:opacity-50 transition-colors duration-200"
        >
          {processing ? 'Сохранение...' : 'Сохранить изменения'}
        </button>
      </form>
    </div>
  );
}

export default UserProfile;
