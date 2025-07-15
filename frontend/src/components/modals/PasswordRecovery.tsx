import React from "react";

const PasswordRecovery: React.FC = ({ isVisible, onClose }) => {
  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-neutral-800 flex items-center justify-center z-50">
      <div className="rounded-lg w-xs p-3 bg-white">
        <div className="flex justify-end">
          <button className="!border-none !p-0 !bg-amber-500 !leading-none" onClick={() => onClose()}>
            &times;
          </button>
        </div>
        <form className="">
          <h2 className="text-2xl mb-1">
            Восстановление пароля
          </h2>
          <label className="text-sm flex flex-col gap-2.5 mb-4">
            Введите ваш email
            <input type="email" placeholder="E-mail" className="border-1 rounded-sm w-full pl-4 pt-2 pb-2" />
          </label>
          <div className="flex justify-between">
            <button className="!bg-blue-600 text-white">
              Отправить ссылку
            </button>
            <button className="!bg-white" onClick={() => onClose()}>
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default PasswordRecovery;
