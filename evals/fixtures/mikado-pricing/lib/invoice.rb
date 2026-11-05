# frozen_string_literal: true

require_relative "legacy_pricer"

class Invoice
  def initialize(order)
    @order = order
  end

  def total_pence
    LegacyPricer.price(@order)
  end

  def summary
    "Order #{@order.id}: #{@order.lines.size} lines, #{total_pence}p"
  end
end
