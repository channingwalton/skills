# frozen_string_literal: true

# The old pricer. It keeps the tax rate in its own constant.
class LegacyPricer
  TAX_PERCENT = 20

  def self.price(order)
    subtotal = order.lines.sum { |line| line.unit_pence * line.quantity }
    subtotal + (subtotal * TAX_PERCENT / 100)
  end
end
