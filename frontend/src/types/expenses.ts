export type ExpenseCategory = {
  id: number;
  name: string;
  slug: string;
  icon: string;
  color: string;
};

export type Expense = {
  id: number;
  user_id: number;
  category_id: number;
  amount: number;
  description: string;
  payment_method: string;
  spent_on: string;
  note: string | null;
  created_at: string;
  updated_at: string;
  category: ExpenseCategory;
};

export type ExpenseCreateInput = {
  category_id: number;
  amount: number;
  description: string;
  payment_method: string;
  spent_on: string;
  note?: string | null;
};

export type ExpenseUpdateInput = Partial<ExpenseCreateInput>;

export type ExpenseListResponse = {
  items: Expense[];
  total: number;
};

export type ExpenseSummaryCategoryBreakdown = {
  category: ExpenseCategory;
  amount: number;
  percentage: number;
};

export type ExpenseSummary = {
  period_start: string;
  period_end: string;
  today_total: number;
  week_total: number;
  month_total: number;
  average_daily: number;
  total_expenses: number;
  top_category: ExpenseSummaryCategoryBreakdown | null;
  category_breakdown: ExpenseSummaryCategoryBreakdown[];
  recent_expenses: Expense[];
};
