# frozen_string_literal: true

Line = Struct.new(:sku, :unit_pence, :quantity)

class Order
  attr_reader :id, :lines

  def initialize(id:, lines:)
    @id = id
    @lines = lines
  end
end
