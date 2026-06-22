import { FormEvent, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  createExpense,
  createIncome,
  deleteExpense,
  deleteIncome,
  getExpenseCategories,
  getExpenseSummary,
  getExpenses,
  getIncomeCategories,
  getIncomeSummary,
  getIncomes,
} from "../lib/api";
import type { Expense, ExpenseCategory, ExpenseSummary } from "../types/expenses";
import type { Income, IncomeCategory, IncomeSummary } from "../types/incomes";
import { useAuth } from "../hooks/useAuth";

type ExpenseFormState = {
  category_id: string;
  amount: string;
  description: string;
  payment_method: string;
  spent_on: string;
  note: string;
};

type IncomeFormState = {
  category_id: string;
  amount: string;
  description: string;
  source: string;
  received_on: string;
  note: string;
};

const paymentMethods = [
  "Tarjeta",
  "Efectivo",
  "Transferencia",
  "Bizum",
  "Domiciliación",
];

const incomeSources = ["Transferencia", "Efectivo", "Bizum", "Nómina", "Otro"];

function formatCurrency(value: number) {
  return new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 2,
  }).format(value);
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("es-ES", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

function formatCompactDate(value: string) {
  return new Intl.DateTimeFormat("es-ES", {
    day: "2-digit",
    month: "short",
  }).format(new Date(value));
}

function getTodayValue() {
  return new Date().toISOString().slice(0, 10);
}

function emptyForm(categoryId = ""): ExpenseFormState {
  return {
    category_id: categoryId,
    amount: "",
    description: "",
    payment_method: "Tarjeta",
    spent_on: getTodayValue(),
    note: "",
  };
}

function emptyIncomeForm(categoryId = ""): IncomeFormState {
  return {
    category_id: categoryId,
    amount: "",
    description: "",
    source: "Transferencia",
    received_on: getTodayValue(),
    note: "",
  };
}

function StatCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <article className="stat-card">
      <span className="stat-label">{label}</span>
      <strong className="stat-value">{value}</strong>
      <span className="stat-hint">{hint}</span>
    </article>
  );
}

function ExpenseRow({
  expense,
  onDelete,
}: {
  expense: Expense;
  onDelete: (expenseId: number) => void;
}) {
  return (
    <li className="expense-row">
      <div className="expense-row__main">
        <span
          className="expense-chip"
          style={{ backgroundColor: `${expense.category.color}22`, color: expense.category.color }}
        >
          <span className="expense-chip__icon">{expense.category.icon}</span>
          {expense.category.name}
        </span>
        <div>
          <h3>{expense.description}</h3>
          <p>
            {expense.payment_method} · {formatDate(expense.spent_on)}
          </p>
          {expense.note ? <small>{expense.note}</small> : null}
        </div>
      </div>
      <div className="expense-row__aside">
        <strong>{formatCurrency(expense.amount)}</strong>
        <button
          className="inline-button inline-button--ghost"
          type="button"
          onClick={() => onDelete(expense.id)}
        >
          Eliminar
        </button>
      </div>
    </li>
  );
}

function IncomeRow({
  income,
  onDelete,
}: {
  income: Income;
  onDelete: (incomeId: number) => void;
}) {
  return (
    <li className="expense-row income-row">
      <div className="expense-row__main">
        <span
          className="expense-chip"
          style={{ backgroundColor: `${income.category.color}22`, color: income.category.color }}
        >
          <span className="expense-chip__icon">{income.category.icon}</span>
          {income.category.name}
        </span>
        <div>
          <h3>{income.description}</h3>
          <p>
            {income.source} · {formatDate(income.received_on)}
          </p>
          {income.note ? <small>{income.note}</small> : null}
        </div>
      </div>
      <div className="expense-row__aside">
        <strong className="income-amount">+{formatCurrency(income.amount)}</strong>
        <button
          className="inline-button inline-button--ghost"
          type="button"
          onClick={() => onDelete(income.id)}
        >
          Eliminar
        </button>
      </div>
    </li>
  );
}

export function DashboardPage() {
  const navigate = useNavigate();
  const { logout, token, user } = useAuth();

  const [categories, setCategories] = useState<ExpenseCategory[]>([]);
  const [incomeCategories, setIncomeCategories] = useState<IncomeCategory[]>([]);
  const [summary, setSummary] = useState<ExpenseSummary | null>(null);
  const [incomeSummary, setIncomeSummary] = useState<IncomeSummary | null>(null);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [incomes, setIncomes] = useState<Income[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isExpenseSubmitting, setIsExpenseSubmitting] = useState(false);
  const [isIncomeSubmitting, setIsIncomeSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedExpenseCategoryId, setSelectedExpenseCategoryId] = useState("");
  const [selectedIncomeCategoryId, setSelectedIncomeCategoryId] = useState("");
  const [expenseForm, setExpenseForm] = useState<ExpenseFormState>(emptyForm());
  const [incomeForm, setIncomeForm] = useState<IncomeFormState>(emptyIncomeForm());

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  const loadDashboard = async () => {
    if (!token) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const [
        fetchedCategories,
        fetchedIncomeCategories,
        fetchedSummary,
        fetchedIncomeSummary,
        fetchedExpenses,
        fetchedIncomes,
      ] = await Promise.all([
        getExpenseCategories(token),
        getIncomeCategories(token),
        getExpenseSummary(token),
        getIncomeSummary(token),
        getExpenses(token, { limit: 30 }),
        getIncomes(token, { limit: 30 }),
      ]);

      setCategories(fetchedCategories);
      setIncomeCategories(fetchedIncomeCategories);
      setSummary(fetchedSummary);
      setIncomeSummary(fetchedIncomeSummary);
      setExpenses(fetchedExpenses.items);
      setIncomes(fetchedIncomes.items);

      if (!selectedExpenseCategoryId && fetchedCategories[0]) {
        const firstCategoryId = String(fetchedCategories[0].id);
        setSelectedExpenseCategoryId(firstCategoryId);
        setExpenseForm((currentForm) =>
          currentForm.category_id
            ? currentForm
            : {
                ...currentForm,
                category_id: firstCategoryId,
              },
        );
      }

      if (!selectedIncomeCategoryId && fetchedIncomeCategories[0]) {
        const firstIncomeCategoryId = String(fetchedIncomeCategories[0].id);
        setSelectedIncomeCategoryId(firstIncomeCategoryId);
        setIncomeForm((currentForm) =>
          currentForm.category_id
            ? currentForm
            : {
                ...currentForm,
                category_id: firstIncomeCategoryId,
              },
        );
      }
    } catch (caughtError) {
      const message =
        caughtError instanceof Error ? caughtError.message : "No se pudo cargar el panel";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void loadDashboard();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  useEffect(() => {
    if (selectedExpenseCategoryId || !categories[0]) {
      return;
    }

    const firstCategoryId = String(categories[0].id);
    setSelectedExpenseCategoryId(firstCategoryId);
    setExpenseForm((currentForm) =>
      currentForm.category_id
        ? currentForm
        : {
            ...currentForm,
            category_id: firstCategoryId,
          },
    );
  }, [categories, selectedExpenseCategoryId]);

  useEffect(() => {
    if (!selectedExpenseCategoryId) {
      return;
    }

    setExpenseForm((currentForm) =>
      currentForm.category_id
        ? currentForm
        : {
            ...currentForm,
            category_id: selectedExpenseCategoryId,
          },
    );
  }, [selectedExpenseCategoryId]);

  useEffect(() => {
    if (selectedIncomeCategoryId || !incomeCategories[0]) {
      return;
    }

    const firstIncomeCategoryId = String(incomeCategories[0].id);
    setSelectedIncomeCategoryId(firstIncomeCategoryId);
    setIncomeForm((currentForm) =>
      currentForm.category_id
        ? currentForm
        : {
            ...currentForm,
            category_id: firstIncomeCategoryId,
          },
    );
  }, [incomeCategories, selectedIncomeCategoryId]);

  useEffect(() => {
    if (!selectedIncomeCategoryId) {
      return;
    }

    setIncomeForm((currentForm) =>
      currentForm.category_id
        ? currentForm
        : {
            ...currentForm,
            category_id: selectedIncomeCategoryId,
          },
    );
  }, [selectedIncomeCategoryId]);

  const categoryMap = useMemo(
    () => new Map(categories.map((category) => [category.id, category])),
    [categories],
  );
  const incomeCategoryMap = useMemo(
    () => new Map(incomeCategories.map((category) => [category.id, category])),
    [incomeCategories],
  );

  const selectedCategory = categoryMap.get(Number(expenseForm.category_id));
  const selectedIncomeCategory = incomeCategoryMap.get(Number(incomeForm.category_id));
  const topCategory = summary?.top_category?.category ?? null;
  const topIncomeCategory = incomeSummary?.top_category?.category ?? null;
  const netBalance = (incomeSummary?.month_total ?? 0) - (summary?.month_total ?? 0);
  const savingsRate =
    incomeSummary && incomeSummary.month_total > 0
      ? Math.max((netBalance / incomeSummary.month_total) * 100, 0)
      : 0;

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!token) {
      return;
    }

    setIsExpenseSubmitting(true);
    setError(null);

    try {
      await createExpense(token, {
        category_id: Number(expenseForm.category_id),
        amount: Number(expenseForm.amount),
        description: expenseForm.description.trim(),
        payment_method: expenseForm.payment_method,
        spent_on: expenseForm.spent_on,
        note: expenseForm.note.trim() ? expenseForm.note.trim() : null,
      });

      setExpenseForm(emptyForm(expenseForm.category_id));
      await loadDashboard();
    } catch (caughtError) {
      const message =
        caughtError instanceof Error ? caughtError.message : "No se pudo guardar el gasto";
      setError(message);
    } finally {
      setIsExpenseSubmitting(false);
    }
  };

  const handleIncomeSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!token) {
      return;
    }

    setIsIncomeSubmitting(true);
    setError(null);

    try {
      await createIncome(token, {
        category_id: Number(incomeForm.category_id),
        amount: Number(incomeForm.amount),
        description: incomeForm.description.trim(),
        source: incomeForm.source,
        received_on: incomeForm.received_on,
        note: incomeForm.note.trim() ? incomeForm.note.trim() : null,
      });

      setIncomeForm(emptyIncomeForm(incomeForm.category_id));
      await loadDashboard();
    } catch (caughtError) {
      const message =
        caughtError instanceof Error ? caughtError.message : "No se pudo guardar el ingreso";
      setError(message);
    } finally {
      setIsIncomeSubmitting(false);
    }
  };

  const handleDelete = async (expenseId: number) => {
    if (!token) {
      return;
    }

    const confirmed = window.confirm("¿Quieres eliminar este gasto?");
    if (!confirmed) {
      return;
    }

    setError(null);

    try {
      await deleteExpense(token, expenseId);
      await loadDashboard();
    } catch (caughtError) {
      const message =
        caughtError instanceof Error ? caughtError.message : "No se pudo eliminar el gasto";
      setError(message);
    }
  };

  const handleIncomeDelete = async (incomeId: number) => {
    if (!token) {
      return;
    }

    const confirmed = window.confirm("¿Quieres eliminar este ingreso?");
    if (!confirmed) {
      return;
    }

    setError(null);

    try {
      await deleteIncome(token, incomeId);
      await loadDashboard();
    } catch (caughtError) {
      const message =
        caughtError instanceof Error ? caughtError.message : "No se pudo eliminar el ingreso";
      setError(message);
    }
  };

  const monthAverage = summary ? summary.average_daily : 0;
  const monthGoal = 1200;
  const monthProgress = summary ? Math.min((summary.month_total / monthGoal) * 100, 100) : 0;

  return (
    <main className="dashboard-shell">
      <div className="dashboard-backdrop" aria-hidden="true" />
      <header className="dashboard-header">
        <div className="dashboard-title">
          <p className="eyebrow">CarePocket · Control diario</p>
          <h1>Gastos del día a día, con lectura profesional.</h1>
          <p>
            Un panel para registrar compras, ver patrones y entender en qué se va el dinero
            con una vista clara, rápida y útil.
          </p>
        </div>
        <div className="dashboard-actions">
          <div className="user-badge">
            <span>Sesión activa</span>
            <strong>{user?.full_name}</strong>
          </div>
          <button className="secondary-button" type="button" onClick={handleLogout}>
            Cerrar sesión
          </button>
        </div>
      </header>

      {error ? <div className="alert alert-error dashboard-alert">{error}</div> : null}

      <section className="hero-panel">
        <div className="hero-panel__copy">
          <p className="eyebrow">Visión general</p>
          <h2>
            {summary ? formatCurrency(summary.month_total) : "0,00 €"} gastados este mes
          </h2>
          <p>
            {summary
              ? `Llevas ${summary.total_expenses} movimientos registrados. El gasto medio diario es ${formatCurrency(
                  monthAverage,
                )}.`
              : "Carga inicial de datos en curso."}
          </p>
        </div>
        <div className="hero-panel__meter">
          <div className="meter-track" aria-hidden="true">
            <div className="meter-fill" style={{ width: `${monthProgress}%` }} />
          </div>
          <div className="meter-caption">
            <span>Límite de referencia mensual</span>
            <strong>{formatCurrency(monthGoal)}</strong>
          </div>
        </div>
      </section>

      <section className="stats-grid">
        <StatCard
          label="Hoy"
          value={summary ? formatCurrency(summary.today_total) : "0,00 €"}
          hint="Lo que has gastado en el día"
        />
        <StatCard
          label="Esta semana"
          value={summary ? formatCurrency(summary.week_total) : "0,00 €"}
          hint="Acumulado desde el lunes"
        />
        <StatCard
          label="Este mes"
          value={summary ? formatCurrency(summary.month_total) : "0,00 €"}
          hint="Tu gasto principal de seguimiento"
        />
        <StatCard
          label="Media diaria"
          value={summary ? formatCurrency(summary.average_daily) : "0,00 €"}
          hint="Ritmo medio estimado"
        />
        <StatCard
          label="Ingresos mes"
          value={incomeSummary ? formatCurrency(incomeSummary.month_total) : "0,00 €"}
          hint="Entradas registradas este mes"
        />
        <StatCard
          label="Saldo neto"
          value={formatCurrency(netBalance)}
          hint={netBalance >= 0 ? "Más ingresos que gastos" : "Atención: gastas más de lo que entra"}
        />
      </section>

      <section className="dashboard-grid">
        <article className="panel panel--form">
          <div className="panel__header">
            <div>
              <p className="eyebrow">Nuevo gasto</p>
              <h2>Registrar movimiento</h2>
            </div>
            <span className="panel__tag">
              {selectedCategory ? `${selectedCategory.icon} ${selectedCategory.name}` : "Selecciona categoría"}
            </span>
          </div>

          <form className="expense-form" onSubmit={handleSubmit}>
            <label className="field">
              <span>Categoría</span>
              <select
                value={expenseForm.category_id}
                onChange={(event) => {
                  const categoryId = event.target.value;
                  setSelectedExpenseCategoryId(categoryId);
                  setExpenseForm((currentForm) => ({ ...currentForm, category_id: categoryId }));
                }}
                required
              >
                <option value="" disabled>
                  Elige una categoría
                </option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.icon} {category.name}
                  </option>
                ))}
              </select>
            </label>

            <div className="field-grid">
              <label className="field">
                <span>Importe</span>
                  <input
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="12,50"
                  value={expenseForm.amount}
                  onChange={(event) =>
                    setExpenseForm((currentForm) => ({ ...currentForm, amount: event.target.value }))
                  }
                  required
                />
              </label>
              <label className="field">
                <span>Fecha</span>
                <input
                  type="date"
                  value={expenseForm.spent_on}
                  onChange={(event) =>
                    setExpenseForm((currentForm) => ({ ...currentForm, spent_on: event.target.value }))
                  }
                  required
                />
              </label>
            </div>

            <label className="field">
              <span>Descripción</span>
              <input
                type="text"
                maxLength={180}
                placeholder="Cafe con leche, supermercado, bus..."
                value={expenseForm.description}
                onChange={(event) =>
                  setExpenseForm((currentForm) => ({
                    ...currentForm,
                    description: event.target.value,
                  }))
                }
                required
              />
            </label>

            <div className="field-grid">
              <label className="field">
                <span>Método de pago</span>
                <select
                  value={expenseForm.payment_method}
                  onChange={(event) =>
                    setExpenseForm((currentForm) => ({
                      ...currentForm,
                      payment_method: event.target.value,
                    }))
                  }
                >
                  {paymentMethods.map((method) => (
                    <option key={method} value={method}>
                      {method}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>Nota opcional</span>
                <input
                  type="text"
                  maxLength={1000}
                  placeholder="Ej. compra compartida"
                  value={expenseForm.note}
                  onChange={(event) =>
                    setExpenseForm((currentForm) => ({ ...currentForm, note: event.target.value }))
                  }
                />
              </label>
            </div>

            <button className="primary-button" type="submit" disabled={isExpenseSubmitting || isLoading}>
              {isExpenseSubmitting ? "Guardando..." : "Guardar gasto"}
            </button>
          </form>
        </article>

        <article className="panel panel--form panel--income-form">
          <div className="panel__header">
            <div>
              <p className="eyebrow">Nuevo ingreso</p>
              <h2>Registrar entrada</h2>
            </div>
            <span className="panel__tag panel__tag--income">
              {selectedIncomeCategory
                ? `${selectedIncomeCategory.icon} ${selectedIncomeCategory.name}`
                : "Selecciona categoría"}
            </span>
          </div>

          <form className="expense-form" onSubmit={handleIncomeSubmit}>
            <label className="field">
              <span>Categoría</span>
              <select
                value={incomeForm.category_id}
                onChange={(event) => {
                  const categoryId = event.target.value;
                  setSelectedIncomeCategoryId(categoryId);
                  setIncomeForm((currentForm) => ({ ...currentForm, category_id: categoryId }));
                }}
                required
              >
                <option value="" disabled>
                  Elige una categoría
                </option>
                {incomeCategories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.icon} {category.name}
                  </option>
                ))}
              </select>
            </label>

            <div className="field-grid">
              <label className="field">
                <span>Importe</span>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="1250,00"
                  value={incomeForm.amount}
                  onChange={(event) =>
                    setIncomeForm((currentForm) => ({ ...currentForm, amount: event.target.value }))
                  }
                  required
                />
              </label>
              <label className="field">
                <span>Fecha</span>
                <input
                  type="date"
                  value={incomeForm.received_on}
                  onChange={(event) =>
                    setIncomeForm((currentForm) => ({
                      ...currentForm,
                      received_on: event.target.value,
                    }))
                  }
                  required
                />
              </label>
            </div>

            <label className="field">
              <span>Descripción</span>
              <input
                type="text"
                maxLength={180}
                placeholder="Nómina, pago freelance, devolución..."
                value={incomeForm.description}
                onChange={(event) =>
                  setIncomeForm((currentForm) => ({
                    ...currentForm,
                    description: event.target.value,
                  }))
                }
                required
              />
            </label>

            <div className="field-grid">
              <label className="field">
                <span>Origen</span>
                <select
                  value={incomeForm.source}
                  onChange={(event) =>
                    setIncomeForm((currentForm) => ({
                      ...currentForm,
                      source: event.target.value,
                    }))
                  }
                >
                  {incomeSources.map((source) => (
                    <option key={source} value={source}>
                      {source}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>Nota opcional</span>
                <input
                  type="text"
                  maxLength={1000}
                  placeholder="Ej. pago recurrente"
                  value={incomeForm.note}
                  onChange={(event) =>
                    setIncomeForm((currentForm) => ({ ...currentForm, note: event.target.value }))
                  }
                />
              </label>
            </div>

            <button className="primary-button" type="submit" disabled={isIncomeSubmitting || isLoading}>
              {isIncomeSubmitting ? "Guardando..." : "Guardar ingreso"}
            </button>
          </form>
        </article>

        <article className="panel panel--insights">
          <div className="panel__header">
            <div>
              <p className="eyebrow">Lectura rápida</p>
              <h2>Patrón actual</h2>
            </div>
          </div>

          <div className="insight-stack">
            <div className="insight-card">
              <span>Categoría dominante</span>
              <strong>
                {topCategory ? `${topCategory.icon} ${topCategory.name}` : "Sin datos"}
              </strong>
              <p>
                {summary?.top_category
                  ? `${summary.top_category.percentage.toFixed(1)}% del gasto mensual`
                  : "Aún no hay gasto suficiente para calcularla."}
              </p>
            </div>

            <div className="insight-card">
              <span>Gasto medio diario</span>
              <strong>{summary ? formatCurrency(summary.average_daily) : "0,00 €"}</strong>
              <p>
                {summary && summary.average_daily > 0
                  ? "Mantén el ritmo bajo control para no salirte del presupuesto."
                  : "Registra gastos para empezar a medir hábitos."}
              </p>
            </div>

            <div className="insight-card">
              <span>Ingreso medio diario</span>
              <strong>{incomeSummary ? formatCurrency(incomeSummary.average_daily) : "0,00 €"}</strong>
              <p>
                {incomeSummary && incomeSummary.average_daily > 0
                  ? "Te ayuda a ver la estabilidad de tus entradas."
                  : "Registra ingresos para empezar a medir tu flujo."}
              </p>
            </div>

            <div className="insight-card">
              <span>Ahorro estimado</span>
              <strong>{formatCurrency(netBalance)}</strong>
              <p>
                {incomeSummary && summary
                  ? `${savingsRate.toFixed(1)}% de tus ingresos se mantiene como saldo.`
                  : "Saldo calculado con lo registrado hasta ahora."}
              </p>
            </div>

            <div className="insight-card">
              <span>Referencia mensual</span>
              <strong>{formatCurrency(monthGoal)}</strong>
              <p>Usada como objetivo orientativo para esta demo financiera.</p>
            </div>
          </div>

          <div className="category-breakdown">
            <h3>Distribución por categoría</h3>
            {summary?.category_breakdown.length ? (
              <ul className="category-list">
                {summary.category_breakdown.map((item) => (
                  <li key={item.category.id} className="category-item">
                    <div className="category-item__title">
                      <span
                        className="expense-chip"
                        style={{
                          backgroundColor: `${item.category.color}22`,
                          color: item.category.color,
                        }}
                      >
                        {item.category.icon} {item.category.name}
                      </span>
                      <strong>{formatCurrency(item.amount)}</strong>
                    </div>
                    <div className="mini-meter" aria-hidden="true">
                      <div
                        className="mini-meter__fill"
                        style={{ width: `${Math.max(item.percentage, 4)}%`, backgroundColor: item.category.color }}
                      />
                    </div>
                    <span>{item.percentage.toFixed(1)}%</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="empty-state">Todavía no hay categorías con gasto este mes.</p>
            )}
          </div>

          <div className="category-breakdown">
            <h3>Distribución de ingresos</h3>
            {incomeSummary?.category_breakdown.length ? (
              <ul className="category-list">
                {incomeSummary.category_breakdown.map((item) => (
                  <li key={item.category.id} className="category-item">
                    <div className="category-item__title">
                      <span
                        className="expense-chip"
                        style={{
                          backgroundColor: `${item.category.color}22`,
                          color: item.category.color,
                        }}
                      >
                        {item.category.icon} {item.category.name}
                      </span>
                      <strong>{formatCurrency(item.amount)}</strong>
                    </div>
                    <div className="mini-meter" aria-hidden="true">
                      <div
                        className="mini-meter__fill"
                        style={{
                          width: `${Math.max(item.percentage, 4)}%`,
                          backgroundColor: item.category.color,
                        }}
                      />
                    </div>
                    <span>{item.percentage.toFixed(1)}%</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="empty-state">Todavía no hay categorías con ingresos este mes.</p>
            )}
          </div>
        </article>
      </section>

      <section className="panel panel--list">
        <div className="panel__header">
          <div>
            <p className="eyebrow">Movimientos recientes</p>
            <h2>Últimos gastos</h2>
          </div>
          <button className="secondary-button" type="button" onClick={loadDashboard} disabled={isLoading}>
            {isLoading ? "Actualizando..." : "Actualizar"}
          </button>
        </div>

        {isLoading && !summary ? (
          <p className="empty-state">Cargando tu panel financiero...</p>
        ) : expenses.length ? (
          <ul className="expense-list">
            {expenses.map((expense) => (
              <ExpenseRow key={expense.id} expense={expense} onDelete={handleDelete} />
            ))}
          </ul>
        ) : (
          <p className="empty-state">Aún no has registrado gastos. Empieza por el formulario.</p>
        )}

        {summary?.recent_expenses.length ? (
          <div className="recent-strip">
            <span className="recent-strip__label">Tendencia reciente</span>
            <div className="recent-strip__items">
              {summary.recent_expenses.slice(0, 5).map((expense) => (
                <div key={expense.id} className="recent-strip__item">
                  <span>{expense.category.icon}</span>
                  <strong>{formatCurrency(expense.amount)}</strong>
                  <small>{formatCompactDate(expense.spent_on)}</small>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </section>

      <section className="panel panel--list">
        <div className="panel__header">
          <div>
            <p className="eyebrow">Ingresos recientes</p>
            <h2>Últimas entradas</h2>
          </div>
          <button className="secondary-button" type="button" onClick={loadDashboard} disabled={isLoading}>
            {isLoading ? "Actualizando..." : "Actualizar"}
          </button>
        </div>

        {isLoading && !incomeSummary ? (
          <p className="empty-state">Cargando tus ingresos...</p>
        ) : incomes.length ? (
          <ul className="expense-list">
            {incomes.map((income) => (
              <IncomeRow key={income.id} income={income} onDelete={handleIncomeDelete} />
            ))}
          </ul>
        ) : (
          <p className="empty-state">Aún no has registrado ingresos. Empieza por el formulario.</p>
        )}

        {incomeSummary?.recent_incomes.length ? (
          <div className="recent-strip">
            <span className="recent-strip__label">Tendencia reciente</span>
            <div className="recent-strip__items">
              {incomeSummary.recent_incomes.slice(0, 5).map((income) => (
                <div key={income.id} className="recent-strip__item">
                  <span>{income.category.icon}</span>
                  <strong>+{formatCurrency(income.amount)}</strong>
                  <small>{formatCompactDate(income.received_on)}</small>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </section>
    </main>
  );
}
