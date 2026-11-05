# frozen_string_literal: true

require_relative "legacy_pricer"

class OrderService
  def checkout(order)
    { order_id: order.id, total_pence: LegacyPricer.price(order) }
  end
end
